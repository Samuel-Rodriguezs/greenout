"""MVCC com snapshot isolation (first-committer-wins) e coleta de versões obsoletas."""
from __future__ import annotations

from typing import Any, Optional

APAGADO = object()


class ErroConflito(Exception):
    """Conflito escrita-escrita: outra transação comitou a mesma chave após o snapshot."""


class ErroTransacao(Exception):
    pass


class Versao:
    __slots__ = ("valor", "ts")

    def __init__(self, valor: Any, ts: int) -> None:
        self.valor = valor
        self.ts = ts  # timestamp de commit

    def __repr__(self) -> str:
        return f"Versao({self.valor!r}, ts={self.ts})"


class Transacao:
    def __init__(self, banco: "BancoMVCC", id_: int, snapshot: int) -> None:
        self.banco = banco
        self.id = id_
        self.snapshot = snapshot
        self.escritas: dict[Any, Any] = {}
        self.ativa = True

    def _checar(self) -> None:
        if not self.ativa:
            raise ErroTransacao(f"transação {self.id} encerrada")

    def ler(self, chave: Any, padrao: Optional[Any] = None) -> Any:
        self._checar()
        if chave in self.escritas:
            v = self.escritas[chave]
            return padrao if v is APAGADO else v
        v = self.banco._visivel(chave, self.snapshot)
        return padrao if v is None or v.valor is APAGADO else v.valor

    def escrever(self, chave: Any, valor: Any) -> None:
        self._checar()
        self.escritas[chave] = valor

    def apagar(self, chave: Any) -> None:
        self._checar()
        self.escritas[chave] = APAGADO

    def chaves(self) -> list[Any]:
        self._checar()
        saida = set()
        for k in set(self.banco.versoes) | set(self.escritas):
            if self.ler(k, APAGADO) is not APAGADO:
                saida.add(k)
        return sorted(saida)

    def commit(self) -> int:
        self._checar()
        self.ativa = False
        self.banco._ativas.pop(self.id, None)
        for k in self.escritas:
            ult = self.banco._ultima(k)
            if ult is not None and ult.ts > self.snapshot:
                raise ErroConflito(f"chave {k!r} alterada por transação concorrente")
        if not self.escritas:
            return self.snapshot
        self.banco.relogio += 1
        for k, v in self.escritas.items():
            self.banco.versoes.setdefault(k, []).append(Versao(v, self.banco.relogio))
        return self.banco.relogio

    def abortar(self) -> None:
        if self.ativa:
            self.ativa = False
            self.banco._ativas.pop(self.id, None)
            self.escritas.clear()


class BancoMVCC:
    def __init__(self) -> None:
        self.versoes: dict[Any, list[Versao]] = {}
        self.relogio = 0
        self._prox = 1
        self._ativas: dict[int, Transacao] = {}

    def iniciar(self) -> Transacao:
        t = Transacao(self, self._prox, self.relogio)
        self._prox += 1
        self._ativas[t.id] = t
        return t

    def _visivel(self, chave: Any, snapshot: int) -> Optional[Versao]:
        for v in reversed(self.versoes.get(chave, [])):
            if v.ts <= snapshot:
                return v
        return None

    def _ultima(self, chave: Any) -> Optional[Versao]:
        vs = self.versoes.get(chave)
        return vs[-1] if vs else None

    def coletar_lixo(self) -> int:
        """Remove versões que nenhuma transação ativa (nem futura) consegue enxergar."""
        horizonte = min((t.snapshot for t in self._ativas.values()), default=self.relogio)
        removidas = 0
        for k in list(self.versoes):
            vs = self.versoes[k]
            # a versão visível no horizonte e as posteriores precisam ficar
            idx = 0
            for i, v in enumerate(vs):
                if v.ts <= horizonte:
                    idx = i
            novos = vs[idx:]
            if len(novos) == 1 and novos[0].valor is APAGADO:
                novos = []
            removidas += len(vs) - len(novos)
            if novos:
                self.versoes[k] = novos
            else:
                del self.versoes[k]
        return removidas

    def total_versoes(self) -> int:
        return sum(len(v) for v in self.versoes.values())
