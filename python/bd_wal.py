"""Write-ahead log com redo/undo (estilo ARIES simplificado) e recuperação após falha.

* Política steal/no-force: páginas sujas podem ir ao disco antes do commit, mas só
  depois de o log até o LSN da página ter sido forçado (regra WAL).
* Commit força o log. Recuperação: redo de tudo que o disco ainda não tem
  (repetir a história) e undo dos perdedores, gravando CLRs (idempotente).
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional


class LogDurable:
    """Log em arquivo JSON-lines. O que não foi forçado (flush) se perde no crash."""

    def __init__(self, caminho: str) -> None:
        self.caminho = caminho
        self.duravel: list[dict] = []
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    try:
                        self.duravel.append(json.loads(linha))
                    except json.JSONDecodeError:
                        break  # cauda rasgada (escrita parcial): ignora
        self.buffer: list[dict] = []
        self.proximo_lsn = (self.duravel[-1]["lsn"] + 1) if self.duravel else 1

    @property
    def lsn_forcado(self) -> int:
        return self.duravel[-1]["lsn"] if self.duravel else 0

    def anexar(self, **campos: Any) -> int:
        reg = {"lsn": self.proximo_lsn, **campos}
        self.proximo_lsn += 1
        self.buffer.append(reg)
        return reg["lsn"]

    def forcar(self, ate_lsn: Optional[int] = None) -> None:
        if not self.buffer:
            return
        alvo = ate_lsn if ate_lsn is not None else self.buffer[-1]["lsn"]
        n = 0
        while n < len(self.buffer) and self.buffer[n]["lsn"] <= alvo:
            n += 1
        escrever, self.buffer = self.buffer[:n], self.buffer[n:]
        with open(self.caminho, "a", encoding="utf-8") as f:
            for r in escrever:
                f.write(json.dumps(r) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.duravel.extend(escrever)

    def todos(self) -> list[dict]:
        return self.duravel + self.buffer

    def obter(self, lsn: int) -> dict:
        for r in reversed(self.todos()):
            if r["lsn"] == lsn:
                return r
        raise KeyError(lsn)


class Disco:
    """Armazenamento estável simulado: chave -> (valor, page_lsn)."""

    def __init__(self) -> None:
        self.paginas: dict[str, tuple[Any, int]] = {}

    def lsn(self, chave: str) -> int:
        return self.paginas.get(chave, (None, 0))[1]

    def gravar(self, chave: str, valor: Any, lsn: int) -> None:
        if valor is None:
            self.paginas[chave] = (None, lsn)
        else:
            self.paginas[chave] = (valor, lsn)

    def valores(self) -> dict[str, Any]:
        return {k: v for k, (v, _) in self.paginas.items() if v is not None}


class BancoWAL:
    def __init__(self, caminho_log: str, disco: Optional[Disco] = None) -> None:
        self.log = LogDurable(caminho_log)
        self.disco = disco if disco is not None else Disco()
        self.cache: dict[str, tuple[Any, int]] = {}
        self.txs: dict[int, int] = {}  # tx ativa -> último lsn
        self._prox_tx = 1 + max([r.get("tx", 0) for r in self.log.todos()] + [0])

    # ---- operações normais ----
    def iniciar(self) -> int:
        tx = self._prox_tx
        self._prox_tx += 1
        self.txs[tx] = self.log.anexar(tipo="BEGIN", tx=tx, prev=0)
        return tx

    def ler(self, chave: str) -> Any:
        if chave in self.cache:
            return self.cache[chave][0]
        return self.disco.paginas.get(chave, (None, 0))[0]

    def escrever(self, tx: int, chave: str, valor: Any) -> None:
        if tx not in self.txs:
            raise KeyError(f"transação {tx} não está ativa")
        lsn = self.log.anexar(tipo="UPDATE", tx=tx, prev=self.txs[tx], chave=chave,
                              antes=self.ler(chave), depois=valor)
        self.txs[tx] = lsn
        self.cache[chave] = (valor, lsn)

    def commit(self, tx: int) -> None:
        if tx not in self.txs:
            raise KeyError(f"transação {tx} não está ativa")
        lsn = self.log.anexar(tipo="COMMIT", tx=tx, prev=self.txs[tx])
        self.log.forcar(lsn)  # durabilidade
        self.log.anexar(tipo="END", tx=tx, prev=lsn)
        del self.txs[tx]

    def abortar(self, tx: int) -> None:
        if tx not in self.txs:
            raise KeyError(f"transação {tx} não está ativa")
        lsn = self.log.anexar(tipo="ABORT", tx=tx, prev=self.txs[tx])
        atual = self.txs[tx]
        while atual:
            r = self.log.obter(atual)
            if r["tipo"] == "UPDATE":
                lsn = self.log.anexar(tipo="CLR", tx=tx, prev=lsn, chave=r["chave"],
                                      depois=r["antes"], desfazer_prox=r["prev"])
                self.cache[r["chave"]] = (r["antes"], lsn)
                atual = r["prev"]
            elif r["tipo"] == "CLR":
                atual = r["desfazer_prox"]
            else:
                atual = r["prev"]
        self.log.anexar(tipo="END", tx=tx, prev=lsn)
        del self.txs[tx]

    def descarregar(self, chave: str) -> None:
        """Grava a página suja no disco, respeitando a regra WAL."""
        if chave not in self.cache:
            return
        valor, lsn = self.cache[chave]
        self.log.forcar(lsn)
        self.disco.gravar(chave, valor, lsn)
        del self.cache[chave]

    def descarregar_tudo(self) -> None:
        for chave in list(self.cache):
            self.descarregar(chave)

    # ---- falha e recuperação ----
    def crash(self) -> "BancoWAL":
        """Perde memória (cache, buffer de log, transações). O disco e o log forçado sobrevivem."""
        return BancoWAL(self.log.caminho, self.disco)

    def recuperar(self) -> dict[str, list[int]]:
        registros = self.log.todos()
        ativos: dict[int, int] = {}
        for r in registros:
            if r["tipo"] == "CHECKPOINT":
                continue
            if r["tipo"] == "END":
                ativos.pop(r["tx"], None)
            else:
                ativos[r["tx"]] = r["lsn"]
        # REDO: repete a história para tudo que o disco ainda não reflete
        refeitos = []
        for r in registros:
            if r["tipo"] in ("UPDATE", "CLR") and self.disco.lsn(r["chave"]) < r["lsn"]:
                self.disco.gravar(r["chave"], r["depois"], r["lsn"])
                refeitos.append(r["lsn"])
        # UNDO: desfaz os perdedores (sem COMMIT) em ordem decrescente de LSN
        commitados = {r["tx"] for r in registros if r["tipo"] == "COMMIT"}
        perdedores = {tx for tx in ativos if tx not in commitados}
        pendentes = {tx: ativos[tx] for tx in perdedores}
        ultimo = dict(pendentes)
        desfeitos = []
        while pendentes:
            tx = max(pendentes, key=lambda t: pendentes[t])
            r = self.log.obter(pendentes[tx])
            if r["tipo"] == "UPDATE":
                lsn = self.log.anexar(tipo="CLR", tx=tx, prev=ultimo[tx], chave=r["chave"],
                                      depois=r["antes"], desfazer_prox=r["prev"])
                ultimo[tx] = lsn
                self.disco.gravar(r["chave"], r["antes"], lsn)
                desfeitos.append(r["lsn"])
                prox = r["prev"]
            elif r["tipo"] == "CLR":
                prox = r["desfazer_prox"]
            else:
                prox = r["prev"]
            if prox:
                pendentes[tx] = prox
            else:
                self.log.anexar(tipo="END", tx=tx, prev=ultimo[tx])
                del pendentes[tx]
        self.log.forcar()
        self.cache.clear()
        self.txs.clear()
        return {"refeitos": refeitos, "desfeitos": desfeitos, "perdedores": sorted(perdedores)}
