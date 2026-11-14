"""Conjunto disjunto (union-find) com compressão de caminho e união por tamanho."""
from __future__ import annotations

from typing import List


class UnionFind:
    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n deve ser >= 0")
        self._pai: List[int] = list(range(n))
        self._tam: List[int] = [1] * n
        self._componentes = n

    @property
    def componentes(self) -> int:
        return self._componentes

    def _checar(self, x: int) -> None:
        if not 0 <= x < len(self._pai):
            raise IndexError(f"elemento fora do intervalo: {x}")

    def encontrar(self, x: int) -> int:
        self._checar(x)
        raiz = x
        while self._pai[raiz] != raiz:
            raiz = self._pai[raiz]
        while self._pai[x] != raiz:
            self._pai[x], x = raiz, self._pai[x]
        return raiz

    def unir(self, a: int, b: int) -> bool:
        """Une os conjuntos; retorna False se já estavam unidos."""
        ra, rb = self.encontrar(a), self.encontrar(b)
        if ra == rb:
            return False
        if self._tam[ra] < self._tam[rb]:
            ra, rb = rb, ra
        self._pai[rb] = ra
        self._tam[ra] += self._tam[rb]
        self._componentes -= 1
        return True

    def conectados(self, a: int, b: int) -> bool:
        return self.encontrar(a) == self.encontrar(b)

    def tamanho(self, x: int) -> int:
        return self._tam[self.encontrar(x)]
