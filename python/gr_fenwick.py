"""Fenwick tree (árvore indexada binária) para somas de prefixo."""

from __future__ import annotations

from typing import Sequence


class Fenwick:
    def __init__(self, dados: Sequence[int] | int = 0) -> None:
        if isinstance(dados, int):
            self._n = dados
            self._t = [0] * (dados + 1)
        else:
            self._n = len(dados)
            self._t = [0] + list(dados)
            for i in range(1, self._n + 1):
                j = i + (i & -i)
                if j <= self._n:
                    self._t[j] += self._t[i]

    def __len__(self) -> int:
        return self._n

    def somar(self, i: int, delta: int) -> None:
        """Adiciona delta ao elemento de índice i (base 0)."""
        if not 0 <= i < self._n:
            raise IndexError(i)
        i += 1
        while i <= self._n:
            self._t[i] += delta
            i += i & -i

    def prefixo(self, i: int) -> int:
        """Soma dos elementos [0, i)."""
        if not 0 <= i <= self._n:
            raise IndexError(i)
        s = 0
        while i > 0:
            s += self._t[i]
            i -= i & -i
        return s

    def intervalo(self, esq: int, dir: int) -> int:
        """Soma sobre [esq, dir)."""
        if esq > dir:
            raise IndexError("intervalo inválido")
        return self.prefixo(dir) - self.prefixo(esq)

    def menor_indice_com_prefixo(self, alvo: int) -> int:
        """Menor i (base 0) tal que soma [0, i] >= alvo, assumindo valores não negativos; -1 se não existe."""
        if alvo <= 0:
            return 0 if self._n else -1
        pos = 0
        passo = 1 << self._n.bit_length()
        while passo:
            nxt = pos + passo
            if nxt <= self._n and self._t[nxt] < alvo:
                pos = nxt
                alvo -= self._t[nxt]
            passo >>= 1
        return pos if pos < self._n else -1
