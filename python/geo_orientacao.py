"""Orientação de três pontos com aritmética exata (Fraction)."""
from __future__ import annotations

from fractions import Fraction

Ponto = tuple[float, float]


def cruzado(o: Ponto, a: Ponto, b: Ponto) -> Fraction:
    """Produto vetorial (a-o) x (b-o), exato."""
    ox, oy = Fraction(o[0]), Fraction(o[1])
    return (Fraction(a[0]) - ox) * (Fraction(b[1]) - oy) - (Fraction(a[1]) - oy) * (
        Fraction(b[0]) - ox
    )


def orientacao(a: Ponto, b: Ponto, c: Ponto) -> int:
    """+1 anti-horário, -1 horário, 0 colineares."""
    v = cruzado(a, b, c)
    return (v > 0) - (v < 0)


def colineares(a: Ponto, b: Ponto, c: Ponto) -> bool:
    return orientacao(a, b, c) == 0


def no_segmento(a: Ponto, b: Ponto, p: Ponto) -> bool:
    """True se p está sobre o segmento fechado ab."""
    if orientacao(a, b, p) != 0:
        return False
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(
        a[1], b[1]
    )


def sentido_poligono(pontos: list[Ponto]) -> int:
    """+1 se anti-horário, -1 se horário, 0 se degenerado (área nula)."""
    if len(pontos) < 3:
        return 0
    soma = Fraction(0)
    for i, (x1, y1) in enumerate(pontos):
        x2, y2 = pontos[(i + 1) % len(pontos)]
        soma += Fraction(x1) * Fraction(y2) - Fraction(x2) * Fraction(y1)
    return (soma > 0) - (soma < 0)
