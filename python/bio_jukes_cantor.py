"""Distância evolutiva de Jukes-Cantor."""

import math


def p_distancia(a: str, b: str) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("sequências vazias ou de tamanhos diferentes")
    return sum(x != y for x, y in zip(a, b)) / len(a)


def distancia(a: str, b: str) -> float:
    """d = -3/4 * ln(1 - 4p/3); exige p < 0,75."""
    p = p_distancia(a, b)
    if p >= 0.75:
        raise ValueError("sequências saturadas (p >= 0,75)")
    return -0.75 * math.log(1 - 4 * p / 3)


def matriz_distancias(seqs: list[str]) -> list[list[float]]:
    n = len(seqs)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j] = m[j][i] = distancia(seqs[i], seqs[j])
    return m
