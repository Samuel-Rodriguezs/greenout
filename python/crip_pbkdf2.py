"""PBKDF2-HMAC (RFC 8018) simples. Didático; use hashlib.pbkdf2_hmac em produção."""
from __future__ import annotations

import hashlib
import hmac
import struct


def pbkdf2(senha: bytes, sal: bytes, iteracoes: int, tamanho: int, algoritmo: str = "sha256") -> bytes:
    if iteracoes < 1 or tamanho < 1:
        raise ValueError("iteracoes e tamanho devem ser >= 1")
    hlen = hashlib.new(algoritmo).digest_size
    saida = b""
    for i in range(1, -(-tamanho // hlen) + 1):
        u = hmac.new(senha, sal + struct.pack(">I", i), algoritmo).digest()
        t = int.from_bytes(u, "big")
        for _ in range(iteracoes - 1):
            u = hmac.new(senha, u, algoritmo).digest()
            t ^= int.from_bytes(u, "big")
        saida += t.to_bytes(hlen, "big")
    return saida[:tamanho]
