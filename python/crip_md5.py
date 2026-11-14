"""MD5 puro em Python (RFC 1321).

AVISO: didático. MD5 está quebrado para fins de segurança; não use em produção.
"""
from __future__ import annotations

import math
import struct

_MASK = 0xFFFFFFFF
_S = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4
_K = [int(abs(math.sin(i + 1)) * 2**32) & _MASK for i in range(64)]


def _rol(x: int, n: int) -> int:
    x &= _MASK
    return ((x << n) | (x >> (32 - n))) & _MASK


def md5(dados: bytes) -> bytes:
    bits = len(dados) * 8
    msg = dados + b"\x80"
    msg += b"\x00" * ((56 - len(msg)) % 64)
    msg += struct.pack("<Q", bits)
    a0, b0, c0, d0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    for off in range(0, len(msg), 64):
        m = struct.unpack("<16I", msg[off : off + 64])
        a, b, c, d = a0, b0, c0, d0
        for i in range(64):
            if i < 16:
                f, g = (b & c) | (~b & d), i
            elif i < 32:
                f, g = (d & b) | (~d & c), (5 * i + 1) % 16
            elif i < 48:
                f, g = b ^ c ^ d, (3 * i + 5) % 16
            else:
                f, g = c ^ (b | (~d & _MASK)), (7 * i) % 16
            f = (f + a + _K[i] + m[g]) & _MASK
            a, d, c = d, c, b
            b = (b + _rol(f, _S[i])) & _MASK
        a0, b0, c0, d0 = (a0 + a) & _MASK, (b0 + b) & _MASK, (c0 + c) & _MASK, (d0 + d) & _MASK
    return struct.pack("<4I", a0, b0, c0, d0)


def md5_hex(dados: bytes) -> str:
    return md5(dados).hex()
