"""Gerenciador de bloqueios S/X com two-phase locking e detecção de deadlock.

* `adquirir` não bloqueia a thread: devolve True (concedido) ou False (enfileirado).
* 2PL: depois da primeira liberação a transação entra na fase de encolhimento e
  não pode mais adquirir. `liberar_todos` (strict 2PL) é o uso normal no commit.
* Deadlock: ciclo no grafo "espera-por"; a vítima é a transação mais jovem do ciclo.
"""
from __future__ import annotations

from typing import Optional

S, X = "S", "X"


class ErroFaseEncolhimento(Exception):
    """Aquisição após liberação viola two-phase locking."""


def compativeis(a: str, b: str) -> bool:
    return a == S and b == S


class GerenciadorBloqueios:
    def __init__(self) -> None:
        self.donos: dict[str, dict[int, str]] = {}
        self.filas: dict[str, list[tuple[int, str]]] = {}
        self.esperando: dict[int, str] = {}   # tx -> recurso
        self.encolhendo: set[int] = set()

    def modo(self, tx: int, recurso: str) -> Optional[str]:
        return self.donos.get(recurso, {}).get(tx)

    def _pode_conceder(self, tx: int, recurso: str, modo: str) -> bool:
        return all(compativeis(m, modo) for t, m in self.donos.get(recurso, {}).items() if t != tx)

    def adquirir(self, tx: int, recurso: str, modo: str) -> bool:
        if modo not in (S, X):
            raise ValueError("modo deve ser 'S' ou 'X'")
        if tx in self.encolhendo:
            raise ErroFaseEncolhimento(f"tx {tx} já liberou bloqueios")
        if tx in self.esperando:
            raise RuntimeError(f"tx {tx} já está esperando por {self.esperando[tx]}")
        atual = self.modo(tx, recurso)
        if atual == X or atual == modo:
            return True
        fila = self.filas.setdefault(recurso, [])
        melhora = atual == S and modo == X
        # fila FIFO: quem chega não fura a fila (exceto upgrade, que tem prioridade)
        if self._pode_conceder(tx, recurso, modo) and (not fila or melhora):
            self.donos.setdefault(recurso, {})[tx] = modo
            return True
        if melhora:
            fila.insert(0, (tx, modo))
        else:
            fila.append((tx, modo))
        self.esperando[tx] = recurso
        return False

    def _promover(self, recurso: str) -> list[int]:
        fila = self.filas.get(recurso, [])
        concedidos: list[int] = []
        while fila:
            tx, modo = fila[0]
            if not self._pode_conceder(tx, recurso, modo):
                break
            fila.pop(0)
            self.donos.setdefault(recurso, {})[tx] = modo
            self.esperando.pop(tx, None)
            concedidos.append(tx)
        if not fila:
            self.filas.pop(recurso, None)
        if not self.donos.get(recurso):
            self.donos.pop(recurso, None)
        return concedidos

    def liberar(self, tx: int, recurso: str) -> list[int]:
        if tx not in self.donos.get(recurso, {}):
            raise KeyError(f"tx {tx} não detém {recurso}")
        del self.donos[recurso][tx]
        self.encolhendo.add(tx)
        return self._promover(recurso)

    def liberar_todos(self, tx: int) -> list[int]:
        """Libera tudo e cancela espera pendente. Devolve txs que foram desbloqueadas."""
        concedidos: list[int] = []
        rec_espera = self.esperando.pop(tx, None)
        if rec_espera is not None:
            self.filas[rec_espera] = [e for e in self.filas[rec_espera] if e[0] != tx]
            concedidos += self._promover(rec_espera)
        for recurso in [r for r, d in self.donos.items() if tx in d]:
            del self.donos[recurso][tx]
            concedidos += self._promover(recurso)
        self.encolhendo.discard(tx)
        return concedidos

    def grafo_espera(self) -> dict[int, set[int]]:
        grafo: dict[int, set[int]] = {}
        for recurso, fila in self.filas.items():
            for i, (tx, modo) in enumerate(fila):
                alvos = {t for t, m in self.donos.get(recurso, {}).items()
                         if t != tx and not compativeis(m, modo)}
                alvos |= {t for t, m in fila[:i] if t != tx and not compativeis(m, modo)}
                grafo.setdefault(tx, set()).update(alvos)
        return grafo

    def detectar_deadlock(self) -> Optional[list[int]]:
        """Devolve um ciclo (lista de txs) ou None."""
        grafo = self.grafo_espera()
        cor: dict[int, int] = {}
        pilha: list[int] = []

        def dfs(u: int) -> Optional[list[int]]:
            cor[u] = 1
            pilha.append(u)
            for v in sorted(grafo.get(u, ())):
                if cor.get(v, 0) == 1:
                    return pilha[pilha.index(v):]
                if cor.get(v, 0) == 0:
                    achado = dfs(v)
                    if achado:
                        return achado
            pilha.pop()
            cor[u] = 2
            return None

        for no in sorted(grafo):
            if cor.get(no, 0) == 0:
                achado = dfs(no)
                if achado:
                    return achado
        return None

    def resolver_deadlock(self) -> Optional[int]:
        """Aborta a transação mais jovem (maior id) do ciclo. Devolve a vítima."""
        ciclo = self.detectar_deadlock()
        if ciclo is None:
            return None
        vitima = max(ciclo)
        self.liberar_todos(vitima)
        return vitima
