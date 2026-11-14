"""Segment tree iterativa com operação associativa configurável."""

from __future__ import annotations

from typing import Callable, Sequence, TypeVar

T = TypeVar("T")


class SegmentTree:
    def __init__(self, dados: Sequence[T], op: Callable[[T, T], T] = lambda a, b: a + b, neutro: T = 0) -> None:
        self._n = len(dados)
        self._op = op
        self._neutro = neutro
        self._t: list = [neutro] * (2 * self._n)
        for i, v in enumerate(dados):
            self._t[self._n + i] = v
        for i in range(self._n - 1, 0, -1):
            self._t[i] = op(self._t[2 * i], self._t[2 * i + 1])

    def __len__(self) -> int:
        return self._n

    def atualizar(self, i: int, valor: T) -> None:
        if not 0 <= i < self._n:
            raise IndexError(i)
        i += self._n
        self._t[i] = valor
        while i > 1:
            i //= 2
            self._t[i] = self._op(self._t[2 * i], self._t[2 * i + 1])

    def consultar(self, esq: int, dir: int) -> T:
        """Resultado sobre o intervalo semiaberto [esq, dir). Intervalo vazio devolve o neutro."""
        if not 0 <= esq <= dir <= self._n:
            raise IndexError("intervalo inválido")
        res_e, res_d = self._neutro, self._neutro
        esq += self._n
        dir += self._n
        while esq < dir:
            if esq & 1:
                res_e = self._op(res_e, self._t[esq])
                esq += 1
            if dir & 1:
                dir -= 1
                res_d = self._op(self._t[dir], res_d)
            esq //= 2
            dir //= 2
        return self._op(res_e, res_d)
