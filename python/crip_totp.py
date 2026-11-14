"""HOTP (RFC 4226) e TOTP (RFC 6238).

AVISO: didático; para produção use bibliotecas auditadas.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time


def hotp(chave: bytes, contador: int, digitos: int = 6, algoritmo: str = "sha1") -> str:
    if not 1 <= digitos <= 9:
        raise ValueError("digitos deve estar entre 1 e 9")
    h = hmac.new(chave, struct.pack(">Q", contador), algoritmo).digest()
    off = h[-1] & 0x0F
    n = struct.unpack(">I", h[off : off + 4])[0] & 0x7FFFFFFF
    return str(n % 10**digitos).zfill(digitos)


def totp(
    chave: bytes, agora: float | None = None, passo: int = 30, digitos: int = 6, algoritmo: str = "sha1", t0: int = 0
) -> str:
    agora = time.time() if agora is None else agora
    return hotp(chave, int((agora - t0) // passo), digitos, algoritmo)


def verificar_totp(codigo: str, chave: bytes, agora: float | None = None, janela: int = 1, passo: int = 30) -> bool:
    """Aceita +-`janela` passos (tolerância de relógio)."""
    agora = time.time() if agora is None else agora
    ok = False
    for d in range(-janela, janela + 1):
        esperado = totp(chave, agora + d * passo, passo, len(codigo))
        ok |= hmac.compare_digest(esperado, codigo)
    return ok


def chave_de_base32(texto: str) -> bytes:
    t = texto.replace(" ", "").upper()
    return base64.b32decode(t + "=" * (-len(t) % 8))


def uri_provisionamento(chave: bytes, conta: str, emissor: str) -> str:
    from urllib.parse import quote

    seg = base64.b32encode(chave).decode().rstrip("=")
    return f"otpauth://totp/{quote(emissor)}:{quote(conta)}?secret={seg}&issuer={quote(emissor)}"


_ = hashlib  # algoritmos aceitos: sha1, sha256, sha512
