"""Passeio aleatório em 1D e 2D."""
from __future__ import annotations

import math
import random

Pos2D = tuple[int, int]
PASSOS_2D: list[Pos2D] = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def caminhada_1d(passos: int, rng: random.Random, inicio: int = 0) -> list[int]:
    pos = [inicio]
    for _ in range(passos):
        pos.append(pos[-1] + rng.choice((-1, 1)))
    return pos


def caminhada_2d(passos: int, rng: random.Random) -> list[Pos2D]:
    x = y = 0
    trilha = [(0, 0)]
    for _ in range(passos):
        dx, dy = rng.choice(PASSOS_2D)
        x, y = x + dx, y + dy
        trilha.append((x, y))
    return trilha


def distancia_quadratica_media(passos: int, repeticoes: int, rng: random.Random) -> float:
    """E[d^2] da caminhada 2D; teoricamente igual ao número de passos."""
    return sum(
        (lambda t: t[-1][0] ** 2 + t[-1][1] ** 2)(caminhada_2d(passos, rng)) for _ in range(repeticoes)
    ) / repeticoes


def primeiro_retorno(rng: random.Random, limite: int = 10000) -> int | None:
    """Passos até voltar à origem na caminhada 1D, ou None se não voltar no limite."""
    pos = 0
    for n in range(1, limite + 1):
        pos += rng.choice((-1, 1))
        if pos == 0:
            return n
    return None


def maxima_excursao(trilha: list[int]) -> int:
    return max(abs(p - trilha[0]) for p in trilha)


def distancia_origem(p: Pos2D) -> float:
    return math.hypot(*p)
