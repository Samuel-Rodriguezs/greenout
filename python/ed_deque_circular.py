"""Deque de capacidade fixa sobre buffer circular."""
from __future__ import annotations

from typing import Any, Iterator, List


class DequeCircular:
    def __init__(self, capacidade: int) -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self._buf: List[Any] = [None] * capacidade
        self._inicio = 0
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def __iter__(self) -> Iterator[Any]:
        for i in range(self._tamanho):
            yield self._buf[(self._inicio + i) % len(self._buf)]

    def vazio(self) -> bool:
        return self._tamanho == 0

    def cheio(self) -> bool:
        return self._tamanho == len(self._buf)

    def adicionar_fim(self, valor: Any) -> None:
        if self.cheio():
            raise OverflowError("deque cheio")
        self._buf[(self._inicio + self._tamanho) % len(self._buf)] = valor
        self._tamanho += 1

    def adicionar_inicio(self, valor: Any) -> None:
        if self.cheio():
            raise OverflowError("deque cheio")
        self._inicio = (self._inicio - 1) % len(self._buf)
        self._buf[self._inicio] = valor
        self._tamanho += 1

    def remover_inicio(self) -> Any:
        if self.vazio():
            raise IndexError("deque vazio")
        valor = self._buf[self._inicio]
        self._buf[self._inicio] = None
        self._inicio = (self._inicio + 1) % len(self._buf)
        self._tamanho -= 1
        return valor

    def remover_fim(self) -> Any:
        if self.vazio():
            raise IndexError("deque vazio")
        pos = (self._inicio + self._tamanho - 1) % len(self._buf)
        valor = self._buf[pos]
        self._buf[pos] = None
        self._tamanho -= 1
        return valor
