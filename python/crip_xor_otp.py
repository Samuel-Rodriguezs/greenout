"""XOR e one-time pad.

AVISO: didático. O OTP só é seguro se a chave for aleatória, do tamanho da mensagem
e NUNCA reutilizada; a reutilização é demonstrada em `recuperar_xor_de_mensagens`.
"""
from __future__ import annotations

import secrets
from itertools import cycle


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR de tamanhos iguais."""
    if len(a) != len(b):
        raise ValueError("tamanhos diferentes")
    return bytes(x ^ y for x, y in zip(a, b))


def xor_repetido(dados: bytes, chave: bytes) -> bytes:
    """XOR com chave repetida ciclicamente (cifra fraca)."""
    if not chave:
        raise ValueError("chave vazia")
    return bytes(x ^ y for x, y in zip(dados, cycle(chave)))


def gerar_chave(tamanho: int) -> bytes:
    return secrets.token_bytes(tamanho)


def otp_cifrar(msg: bytes, chave: bytes) -> bytes:
    if len(chave) < len(msg):
        raise ValueError("chave menor que a mensagem")
    return xor_bytes(msg, chave[: len(msg)])


otp_decifrar = otp_cifrar


def recuperar_xor_de_mensagens(c1: bytes, c2: bytes) -> bytes:
    """Com a mesma chave, c1 ^ c2 == m1 ^ m2 (a chave some)."""
    n = min(len(c1), len(c2))
    return xor_bytes(c1[:n], c2[:n])


def quebrar_xor_um_byte(cifrado: bytes) -> tuple[int, bytes]:
    """Força bruta de chave de 1 byte, pontuando por frequência de texto em inglês/português."""
    comuns = b" etaoinsrhldcuEAOIN"
    melhor = (-1, 0, b"")
    for k in range(256):
        txt = bytes(b ^ k for b in cifrado)
        if any(b < 9 or 13 < b < 32 or b > 126 for b in txt):
            continue
        pontos = sum(txt.count(bytes([c])) for c in comuns)
        if pontos > melhor[0]:
            melhor = (pontos, k, txt)
    if melhor[0] < 0:
        raise ValueError("nenhuma chave plausível")
    return melhor[1], melhor[2]
