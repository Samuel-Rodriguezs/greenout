"""Gerador de tokens seguros com `secrets` (hex, urlsafe, alfabeto customizado, código numérico)."""
from __future__ import annotations

import math
import secrets
import string

ALFABETO_ALFANUM = string.ascii_letters + string.digits
ALFABETO_SEM_AMBIGUOS = "".join(c for c in ALFABETO_ALFANUM if c not in "0O1lI")


def token_hex(n_bytes: int = 16) -> str:
    _checar(n_bytes)
    return secrets.token_hex(n_bytes)


def token_urlsafe(n_bytes: int = 16) -> str:
    _checar(n_bytes)
    return secrets.token_urlsafe(n_bytes)


def token_alfabeto(tamanho: int, alfabeto: str = ALFABETO_ALFANUM) -> str:
    _checar(tamanho)
    if len(set(alfabeto)) < 2:
        raise ValueError("alfabeto precisa de >= 2 símbolos distintos")
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))


def codigo_numerico(digitos: int = 6) -> str:
    _checar(digitos)
    return str(secrets.randbelow(10**digitos)).zfill(digitos)


def entropia_bits(tamanho: int, alfabeto: str = ALFABETO_ALFANUM) -> float:
    return tamanho * math.log2(len(set(alfabeto)))


def _checar(n: int) -> None:
    if n < 1:
        raise ValueError("tamanho deve ser >= 1")
