"""SHA-256 puro em Python (FIPS 180-4).

AVISO: implementação didática, para estudo. Não use em produção; use hashlib.
"""
from __future__ import annotations

import math
import struct


def _primos(n: int) -> list[int]:
    ps: list[int] = []
    c = 2
    while len(ps) < n:
        if all(c % p for p in ps if p * p <= c):
            ps.append(c)
        c += 1
    return ps


def _raiz_cubica_inteira(n: int) -> int:
    lo, hi = 0, 1 << ((n.bit_length() // 3) + 2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**3 <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


_MASK = 0xFFFFFFFF
_PRIMOS = _primos(64)
# Constantes: parte fracionária das raízes (cúbicas/quadradas) dos primeiros primos.
K: list[int] = [_raiz_cubica_inteira(p << 96) & _MASK for p in _PRIMOS]
H0: list[int] = [math.isqrt(p << 64) & _MASK for p in _PRIMOS[:8]]


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & _MASK


def _preencher(dados: bytes) -> bytes:
    bits = len(dados) * 8
    dados += b"\x80"
    dados += b"\x00" * ((56 - len(dados)) % 64)
    return dados + struct.pack(">Q", bits)


def sha256(dados: bytes) -> bytes:
    """Retorna o digest de 32 bytes."""
    h = list(H0)
    msg = _preencher(dados)
    for off in range(0, len(msg), 64):
        w = list(struct.unpack(">16I", msg[off : off + 64]))
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ (~e & _MASK & g)
            t1 = (hh + s1 + ch + K[i] + w[i]) & _MASK
            s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (s0 + maj) & _MASK
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & _MASK, c, b, a, (t1 + t2) & _MASK
        h = [(x + y) & _MASK for x, y in zip(h, (a, b, c, d, e, f, g, hh))]
    return struct.pack(">8I", *h)


def sha256_hex(dados: bytes) -> str:
    return sha256(dados).hex()
