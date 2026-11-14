"""Bloom filter para SSTables: sem falsos negativos, falsos positivos controlados."""
from __future__ import annotations

import hashlib
import math
import struct
from typing import Any, Iterable

_CAB = struct.Struct("<II")  # m bits, k hashes


class BloomFilter:
    def __init__(self, m_bits: int, k: int) -> None:
        if m_bits < 1 or k < 1:
            raise ValueError("m_bits e k devem ser >= 1")
        self.m = m_bits
        self.k = k
        self.bits = bytearray((m_bits + 7) // 8)
        self.n = 0

    @classmethod
    def para(cls, n_esperado: int, taxa_fp: float = 0.01) -> "BloomFilter":
        if n_esperado < 1 or not 0 < taxa_fp < 1:
            raise ValueError("parâmetros inválidos")
        m = max(8, math.ceil(-n_esperado * math.log(taxa_fp) / (math.log(2) ** 2)))
        k = max(1, round(m / n_esperado * math.log(2)))
        return cls(m, k)

    def _posicoes(self, item: Any) -> Iterable[int]:
        d = hashlib.blake2b(repr(item).encode("utf-8"), digest_size=16).digest()
        h1 = int.from_bytes(d[:8], "little")
        h2 = int.from_bytes(d[8:], "little") | 1  # ímpar: percorre todas as posições
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def adicionar(self, item: Any) -> None:
        for p in self._posicoes(item):
            self.bits[p >> 3] |= 1 << (p & 7)
        self.n += 1

    def __contains__(self, item: Any) -> bool:
        return all(self.bits[p >> 3] & (1 << (p & 7)) for p in self._posicoes(item))

    def taxa_fp_estimada(self) -> float:
        return (1 - math.exp(-self.k * self.n / self.m)) ** self.k

    def uniao(self, outro: "BloomFilter") -> "BloomFilter":
        if (self.m, self.k) != (outro.m, outro.k):
            raise ValueError("filtros com parâmetros diferentes")
        r = BloomFilter(self.m, self.k)
        r.bits = bytearray(a | b for a, b in zip(self.bits, outro.bits))
        r.n = self.n + outro.n
        return r

    def para_bytes(self) -> bytes:
        return _CAB.pack(self.m, self.k) + bytes(self.bits)

    @classmethod
    def de_bytes(cls, bruto: bytes) -> "BloomFilter":
        if len(bruto) < _CAB.size:
            raise ValueError("dados truncados")
        m, k = _CAB.unpack_from(bruto)
        corpo = bruto[_CAB.size:]
        if m < 1 or k < 1 or len(corpo) != (m + 7) // 8:
            raise ValueError("dados corrompidos")
        f = cls(m, k)
        f.bits = bytearray(corpo)
        return f
