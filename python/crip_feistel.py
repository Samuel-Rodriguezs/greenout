"""Cifra de bloco Feistel simples (64 bits, 8 rodadas) com modos CBC e CTR.

AVISO: cifra inventada para estudo, SEM análise de segurança. Não use em produção.
"""
from __future__ import annotations

import hashlib
import secrets

BLOCO = 8
RODADAS = 8


def _f(metade: bytes, chave: bytes, rodada: int) -> bytes:
    return hashlib.sha256(chave + bytes([rodada]) + metade).digest()[:4]


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def cifrar_bloco(bloco: bytes, chave: bytes) -> bytes:
    if len(bloco) != BLOCO:
        raise ValueError("bloco deve ter 8 bytes")
    e, d = bloco[:4], bloco[4:]
    for r in range(RODADAS):
        e, d = d, _xor(e, _f(d, chave, r))
    return d + e  # troca final desfaz a última permutação


def decifrar_bloco(bloco: bytes, chave: bytes) -> bytes:
    if len(bloco) != BLOCO:
        raise ValueError("bloco deve ter 8 bytes")
    e, d = bloco[:4], bloco[4:]
    for r in reversed(range(RODADAS)):
        e, d = d, _xor(e, _f(d, chave, r))
    return d + e


def pad(dados: bytes) -> bytes:
    n = BLOCO - len(dados) % BLOCO
    return dados + bytes([n]) * n


def unpad(dados: bytes) -> bytes:
    if not dados or len(dados) % BLOCO:
        raise ValueError("tamanho inválido")
    n = dados[-1]
    if not 1 <= n <= BLOCO or dados[-n:] != bytes([n]) * n:
        raise ValueError("padding inválido")
    return dados[:-n]


def cbc_cifrar(dados: bytes, chave: bytes, iv: bytes | None = None) -> bytes:
    """Retorna iv + cifrado."""
    iv = iv if iv is not None else secrets.token_bytes(BLOCO)
    if len(iv) != BLOCO:
        raise ValueError("iv deve ter 8 bytes")
    p = pad(dados)
    saida, anterior = [iv], iv
    for i in range(0, len(p), BLOCO):
        anterior = cifrar_bloco(_xor(p[i : i + BLOCO], anterior), chave)
        saida.append(anterior)
    return b"".join(saida)


def cbc_decifrar(cifrado: bytes, chave: bytes) -> bytes:
    if len(cifrado) < 2 * BLOCO or len(cifrado) % BLOCO:
        raise ValueError("tamanho inválido")
    anterior, saida = cifrado[:BLOCO], []
    for i in range(BLOCO, len(cifrado), BLOCO):
        bloco = cifrado[i : i + BLOCO]
        saida.append(_xor(decifrar_bloco(bloco, chave), anterior))
        anterior = bloco
    return unpad(b"".join(saida))


def ctr(dados: bytes, chave: bytes, nonce: bytes) -> bytes:
    """Modo CTR (cifra e decifra). nonce de 4 bytes + contador de 4 bytes."""
    if len(nonce) != 4:
        raise ValueError("nonce deve ter 4 bytes")
    saida = bytearray()
    for i in range(0, len(dados), BLOCO):
        ks = cifrar_bloco(nonce + (i // BLOCO).to_bytes(4, "big"), chave)
        saida += _xor(dados[i : i + BLOCO], ks)
    return bytes(saida)
