"""Ancestral comum mais baixo (LCA): árvore binária e binary lifting em árvore geral."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class No:
    valor: int
    esq: Optional["No"] = None
    dir: Optional["No"] = None


def lca_binaria(raiz: Optional[No], a: int, b: int) -> Optional[No]:
    """LCA por valores; None se algum dos valores não existe na árvore."""

    def achar(n: Optional[No], x: int) -> bool:
        pilha = [n]
        while pilha:
            c = pilha.pop()
            if c is None:
                continue
            if c.valor == x:
                return True
            pilha.extend((c.esq, c.dir))
        return False

    if not (achar(raiz, a) and achar(raiz, b)):
        return None

    def rec(n: Optional[No]) -> Optional[No]:
        if n is None or n.valor in (a, b):
            return n
        e, d = rec(n.esq), rec(n.dir)
        if e and d:
            return n
        return e or d

    return rec(raiz)


class LcaArvore:
    """Binary lifting para árvore enraizada com nós 0..n-1."""

    def __init__(self, n: int, arestas: list[tuple[int, int]], raiz: int = 0) -> None:
        if n <= 0 or not 0 <= raiz < n:
            raise ValueError("árvore inválida")
        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in arestas:
            adj[u].append(v)
            adj[v].append(u)
        self._log = max(1, n.bit_length())
        self.profundidade = [-1] * n
        self._anc = [[raiz] * n for _ in range(self._log)]
        self.profundidade[raiz] = 0
        fila = deque([raiz])
        while fila:
            u = fila.popleft()
            for v in adj[u]:
                if self.profundidade[v] == -1:
                    self.profundidade[v] = self.profundidade[u] + 1
                    self._anc[0][v] = u
                    fila.append(v)
        if -1 in self.profundidade:
            raise ValueError("grafo não é uma árvore conexa")
        for k in range(1, self._log):
            for v in range(n):
                self._anc[k][v] = self._anc[k - 1][self._anc[k - 1][v]]

    def lca(self, u: int, v: int) -> int:
        if self.profundidade[u] < self.profundidade[v]:
            u, v = v, u
        diff = self.profundidade[u] - self.profundidade[v]
        for k in range(self._log):
            if diff >> k & 1:
                u = self._anc[k][u]
        if u == v:
            return u
        for k in range(self._log - 1, -1, -1):
            if self._anc[k][u] != self._anc[k][v]:
                u, v = self._anc[k][u], self._anc[k][v]
        return self._anc[0][u]

    def distancia(self, u: int, v: int) -> int:
        return self.profundidade[u] + self.profundidade[v] - 2 * self.profundidade[self.lca(u, v)]
