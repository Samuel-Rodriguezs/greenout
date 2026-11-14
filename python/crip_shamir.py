"""Compartilhamento de segredo de Shamir (k de n) sobre corpo primo GF(p).

AVISO: didático; sem verificação de integridade das partes. Não use em produção.
"""
from __future__ import annotations

import secrets

# Primo de Mersenne 2**521 - 1: comporta segredos de até 65 bytes.
PRIMO = 2**521 - 1


def dividir(segredo: int, n: int, k: int, p: int = PRIMO) -> list[tuple[int, int]]:
    """Gera n partes (x, y); quaisquer k reconstroem o segredo."""
    if not 0 <= segredo < p:
        raise ValueError("segredo fora do corpo")
    if not 1 <= k <= n or n >= p:
        raise ValueError("exige 1 <= k <= n")
    coefs = [segredo] + [secrets.randbelow(p) for _ in range(k - 1)]
    partes = []
    for x in range(1, n + 1):
        y = 0
        for c in reversed(coefs):  # Horner
            y = (y * x + c) % p
        partes.append((x, y))
    return partes


def reconstruir(partes: list[tuple[int, int]], p: int = PRIMO) -> int:
    """Interpolação de Lagrange em x = 0."""
    xs = [x for x, _ in partes]
    if not partes or len(set(xs)) != len(xs):
        raise ValueError("partes vazias ou com x repetido")
    total = 0
    for i, (xi, yi) in enumerate(partes):
        num, den = 1, 1
        for j, (xj, _) in enumerate(partes):
            if i != j:
                num = num * (-xj) % p
                den = den * (xi - xj) % p
        total = (total + yi * num * pow(den, -1, p)) % p
    return total


def dividir_bytes(segredo: bytes, n: int, k: int) -> list[tuple[int, int]]:
    if len(segredo) > 65:
        raise ValueError("segredo grande demais (máx. 65 bytes)")
    return dividir(int.from_bytes(b"\x01" + segredo, "big"), n, k)  # \x01 preserva zeros à esquerda


def reconstruir_bytes(partes: list[tuple[int, int]]) -> bytes:
    v = reconstruir(partes)
    return v.to_bytes((v.bit_length() + 7) // 8, "big")[1:]
