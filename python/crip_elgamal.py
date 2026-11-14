"""ElGamal didático sobre Z_p*.

AVISO: apenas para estudo. Sem padding, sem verificação de grupo seguro; não use em produção.
"""
from __future__ import annotations

import random
from typing import NamedTuple

from crip_rsa import eh_primo, inverso_modular


class ChavePublica(NamedTuple):
    p: int
    g: int
    h: int


class ChavePrivada(NamedTuple):
    p: int
    x: int


def gerar_primo_seguro(bits: int, rng: random.Random) -> int:
    """p = 2q + 1 com q primo."""
    while True:
        q = rng.getrandbits(bits - 1) | (1 << (bits - 2)) | 1
        if eh_primo(q) and eh_primo(2 * q + 1):
            return 2 * q + 1


def _gerador(p: int, rng: random.Random) -> int:
    q = (p - 1) // 2
    while True:
        g = rng.randrange(2, p - 1)
        if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
            return g


def gerar_chaves(bits: int = 32, rng: random.Random | None = None) -> tuple[ChavePublica, ChavePrivada]:
    rng = rng or random.Random()
    p = gerar_primo_seguro(bits, rng)
    g = _gerador(p, rng)
    x = rng.randrange(2, p - 1)
    return ChavePublica(p, g, pow(g, x, p)), ChavePrivada(p, x)


def cifrar(m: int, pub: ChavePublica, rng: random.Random | None = None) -> tuple[int, int]:
    if not 1 <= m < pub.p:
        raise ValueError("mensagem fora de [1, p)")
    rng = rng or random.Random()
    k = rng.randrange(2, pub.p - 1)
    return pow(pub.g, k, pub.p), m * pow(pub.h, k, pub.p) % pub.p


def decifrar(c: tuple[int, int], priv: ChavePrivada) -> int:
    c1, c2 = c
    s = pow(c1, priv.x, priv.p)
    return c2 * inverso_modular(s, priv.p) % priv.p
