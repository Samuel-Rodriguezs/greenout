"""Área (fórmula do cadarço/shoelace), perímetro e centroide de polígonos."""
from __future__ import annotations

import math
from fractions import Fraction

Ponto = tuple[float, float]


def area_com_sinal(pontos: list[Ponto]) -> Fraction:
    """Área exata; positiva se anti-horário, negativa se horário."""
    n = len(pontos)
    if n < 3:
        return Fraction(0)
    soma = Fraction(0)
    for i in range(n):
        x1, y1 = pontos[i]
        x2, y2 = pontos[(i + 1) % n]
        soma += Fraction(x1) * Fraction(y2) - Fraction(x2) * Fraction(y1)
    return soma / 2


def area(pontos: list[Ponto]) -> Fraction:
    return abs(area_com_sinal(pontos))


def perimetro(pontos: list[Ponto]) -> float:
    n = len(pontos)
    if n < 2:
        return 0.0
    return sum(math.dist(pontos[i], pontos[(i + 1) % n]) for i in range(n))


def centroide(pontos: list[Ponto]) -> tuple[Fraction, Fraction]:
    """Centroide da região poligonal. Se a área é nula, usa a média dos vértices."""
    if not pontos:
        raise ValueError("polígono vazio")
    a = area_com_sinal(pontos)
    n = len(pontos)
    if a == 0:
        return (
            sum(Fraction(p[0]) for p in pontos) / n,
            sum(Fraction(p[1]) for p in pontos) / n,
        )
    cx = cy = Fraction(0)
    for i in range(n):
        x1, y1 = Fraction(pontos[i][0]), Fraction(pontos[i][1])
        x2, y2 = Fraction(pontos[(i + 1) % n][0]), Fraction(pontos[(i + 1) % n][1])
        c = x1 * y2 - x2 * y1
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    return (cx / (6 * a), cy / (6 * a))


def eh_convexo(pontos: list[Ponto]) -> bool:
    """True se todos os giros têm o mesmo sentido (colineares são tolerados)."""
    n = len(pontos)
    if n < 3:
        return False
    sinal = 0
    for i in range(n):
        ax, ay = pontos[i]
        bx, by = pontos[(i + 1) % n]
        cx, cy = pontos[(i + 2) % n]
        c = (Fraction(bx) - Fraction(ax)) * (Fraction(cy) - Fraction(by)) - (
            Fraction(by) - Fraction(ay)
        ) * (Fraction(cx) - Fraction(bx))
        if c != 0:
            s = 1 if c > 0 else -1
            if sinal and s != sinal:
                return False
            sinal = s
    return sinal != 0
