"""Heap mínimo implementado sobre lista."""
from __future__ import annotations

from typing import Iterable, List


class HeapMinimo:
    def __init__(self, itens: Iterable[int] = ()) -> None:
        self._dados: List[int] = []
        for item in itens:
            self.inserir(item)

    def __len__(self) -> int:
        return len(self._dados)

    def vazio(self) -> bool:
        return not self._dados

    def minimo(self) -> int:
        if not self._dados:
            raise IndexError("heap vazio")
        return self._dados[0]

    def inserir(self, valor: int) -> None:
        d = self._dados
        d.append(valor)
        i = len(d) - 1
        while i > 0:
            pai = (i - 1) // 2
            if d[pai] <= d[i]:
                break
            d[pai], d[i] = d[i], d[pai]
            i = pai

    def extrair(self) -> int:
        d = self._dados
        if not d:
            raise IndexError("heap vazio")
        topo = d[0]
        ultimo = d.pop()
        if d:
            d[0] = ultimo
            i = 0
            while True:
                esq, dir_ = 2 * i + 1, 2 * i + 2
                menor = i
                if esq < len(d) and d[esq] < d[menor]:
                    menor = esq
                if dir_ < len(d) and d[dir_] < d[menor]:
                    menor = dir_
                if menor == i:
                    break
                d[i], d[menor] = d[menor], d[i]
                i = menor
        return topo


def heap_sort(itens: Iterable[int]) -> List[int]:
    heap = HeapMinimo(itens)
    return [heap.extrair() for _ in range(len(heap))]
