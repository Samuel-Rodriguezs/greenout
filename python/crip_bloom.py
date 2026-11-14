"""Filtro de Bloom (dupla hash derivada de SHA-256) com dimensionamento ótimo."""
from __future__ import annotations

import hashlib
import math


class FiltroBloom:
    def __init__(self, bits: int, hashes: int) -> None:
        if bits < 1 or hashes < 1:
            raise ValueError("bits e hashes devem ser >= 1")
        self.bits, self.hashes = bits, hashes
        self._arr = bytearray((bits + 7) // 8)
        self.itens = 0

    @classmethod
    def para(cls, capacidade: int, taxa_falso_positivo: float = 0.01) -> "FiltroBloom":
        if capacidade < 1 or not 0 < taxa_falso_positivo < 1:
            raise ValueError("capacidade >= 1 e 0 < taxa < 1")
        m = math.ceil(-capacidade * math.log(taxa_falso_positivo) / math.log(2) ** 2)
        k = max(1, round(m / capacidade * math.log(2)))
        return cls(m, k)

    def _posicoes(self, item: str | bytes) -> list[int]:
        b = item.encode() if isinstance(item, str) else item
        d = hashlib.sha256(b).digest()
        h1 = int.from_bytes(d[:16], "big")
        h2 = int.from_bytes(d[16:], "big") | 1
        return [(h1 + i * h2) % self.bits for i in range(self.hashes)]

    def adicionar(self, item: str | bytes) -> None:
        for p in self._posicoes(item):
            self._arr[p >> 3] |= 1 << (p & 7)
        self.itens += 1

    def __contains__(self, item: str | bytes) -> bool:
        return all(self._arr[p >> 3] >> (p & 7) & 1 for p in self._posicoes(item))

    def taxa_estimada(self) -> float:
        return (1 - math.exp(-self.hashes * self.itens / self.bits)) ** self.hashes
