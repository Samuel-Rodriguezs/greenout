"""Mediana de fluxo de dados com dois heaps."""

from __future__ import annotations

import heapq


class MedianaFluxo:
    def __init__(self) -> None:
        self._baixos: list[float] = []  # max-heap (valores negados)
        self._altos: list[float] = []  # min-heap

    def __len__(self) -> int:
        return len(self._baixos) + len(self._altos)

    def adicionar(self, x: float) -> None:
        if self._baixos and x > -self._baixos[0]:
            heapq.heappush(self._altos, x)
        else:
            heapq.heappush(self._baixos, -x)
        if len(self._baixos) > len(self._altos) + 1:
            heapq.heappush(self._altos, -heapq.heappop(self._baixos))
        elif len(self._altos) > len(self._baixos):
            heapq.heappush(self._baixos, -heapq.heappop(self._altos))

    def mediana(self) -> float:
        if not self:
            raise ValueError("fluxo vazio")
        if len(self._baixos) > len(self._altos):
            return float(-self._baixos[0])
        return (-self._baixos[0] + self._altos[0]) / 2
