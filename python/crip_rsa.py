"""RSA didático com Miller-Rabin e Euclides estendido.

AVISO: apenas para estudo (sem padding, primos pequenos). Nunca use em produção.
"""
from __future__ import annotations

import random
from typing import NamedTuple

_PEQUENOS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def euclides_estendido(a: int, b: int) -> tuple[int, int, int]:
    """Retorna (g, x, y) com a*x + b*y = g = mdc(a, b)."""
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def inverso_modular(a: int, m: int) -> int:
    g, x, _ = euclides_estendido(a % m, m)
    if g != 1:
        raise ValueError("inverso modular inexistente")
    return x % m


def eh_primo(n: int) -> bool:
    """Miller-Rabin determinístico para n < 3.3e24 (bases primas fixas)."""
    if n < 2:
        return False
    for p in _PEQUENOS:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _PEQUENOS:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gerar_primo(bits: int, rng: random.Random) -> int:
    if bits < 3:
        raise ValueError("bits deve ser >= 3")
    while True:
        c = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if eh_primo(c):
            return c


class ChavesRSA(NamedTuple):
    n: int
    e: int
    d: int


def gerar_chaves(bits: int = 32, rng: random.Random | None = None, e: int = 65537) -> ChavesRSA:
    """Gera chaves com primos de `bits` bits cada."""
    rng = rng or random.Random()
    while True:
        p, q = gerar_primo(bits, rng), gerar_primo(bits, rng)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        ee = e
        if euclides_estendido(ee, phi)[0] != 1:
            ee = 3
            if euclides_estendido(ee, phi)[0] != 1:
                continue
        return ChavesRSA(p * q, ee, inverso_modular(ee, phi))


def cifrar(m: int, n: int, e: int) -> int:
    if not 0 <= m < n:
        raise ValueError("mensagem fora de [0, n)")
    return pow(m, e, n)


def decifrar(c: int, n: int, d: int) -> int:
    return pow(c, d, n)


def assinar(m: int, n: int, d: int) -> int:
    return pow(m, d, n)


def verificar(m: int, assinatura: int, n: int, e: int) -> bool:
    return pow(assinatura, e, n) == m % n
