"""Distância de ponto a reta e a segmento, com ponto mais próximo."""
from __future__ import annotations

import math

Ponto = tuple[float, float]


def distancia(a: Ponto, b: Ponto) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distancia_ponto_reta(p: Ponto, a: Ponto, b: Ponto) -> float:
    """Distância de p à reta infinita por a e b (a == b: distância a a)."""
    comp = distancia(a, b)
    if comp == 0:
        return distancia(p, a)
    cruz = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    return abs(cruz) / comp


def ponto_mais_proximo_no_segmento(p: Ponto, a: Ponto, b: Ponto) -> Ponto:
    dx, dy = b[0] - a[0], b[1] - a[1]
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return a
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / d2
    t = max(0.0, min(1.0, t))
    return (a[0] + t * dx, a[1] + t * dy)


def distancia_ponto_segmento(p: Ponto, a: Ponto, b: Ponto) -> float:
    return distancia(p, ponto_mais_proximo_no_segmento(p, a, b))


def distancia_segmentos(a: Ponto, b: Ponto, c: Ponto, d: Ponto) -> float:
    """Distância mínima entre dois segmentos; 0 se se cruzam."""
    from geo_segmentos import segmentos_se_cruzam

    if segmentos_se_cruzam(a, b, c, d):
        return 0.0
    return min(
        distancia_ponto_segmento(a, c, d),
        distancia_ponto_segmento(b, c, d),
        distancia_ponto_segmento(c, a, b),
        distancia_ponto_segmento(d, a, b),
    )
