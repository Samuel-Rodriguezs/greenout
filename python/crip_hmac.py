"""HMAC (RFC 2104) próprio sobre qualquer hash do hashlib. Didático."""
from __future__ import annotations

import hashlib


def hmac_digest(chave: bytes, msg: bytes, algoritmo: str = "sha256") -> bytes:
    bloco = hashlib.new(algoritmo).block_size
    if len(chave) > bloco:
        chave = hashlib.new(algoritmo, chave).digest()
    chave = chave.ljust(bloco, b"\x00")
    ipad = bytes(b ^ 0x36 for b in chave)
    opad = bytes(b ^ 0x5C for b in chave)
    interno = hashlib.new(algoritmo, ipad + msg).digest()
    return hashlib.new(algoritmo, opad + interno).digest()


def comparar_constante(a: bytes, b: bytes) -> bool:
    """Comparação sem curto-circuito."""
    if len(a) != len(b):
        return False
    r = 0
    for x, y in zip(a, b):
        r |= x ^ y
    return r == 0


def verificar(chave: bytes, msg: bytes, tag: bytes, algoritmo: str = "sha256") -> bool:
    return comparar_constante(hmac_digest(chave, msg, algoritmo), tag)
