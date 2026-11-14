"""Interseções círculo-círculo e círculo-reta/segmento."""
from __future__ import annotations

import math
from dataclasses import dataclass

Ponto = tuple[float, float]
EPS = 1e-9


@dataclass(frozen=True)
class Circulo:
    cx: float
    cy: float
    r: float

    def __post_init__(self) -> None:
        if self.r < 0:
            raise ValueError("raio negativo")

    @property
    def centro(self) -> Ponto:
        return (self.cx, self.cy)


def circulo_circulo(a: Circulo, b: Circulo) -> list[Ponto]:
    """Pontos de interseção das circunferências: 0, 1 ou 2.

    Círculos idênticos (infinitos pontos) levantam ValueError.
    """
    dx, dy = b.cx - a.cx, b.cy - a.cy
    d = math.hypot(dx, dy)
    if d < EPS and abs(a.r - b.r) < EPS:
        raise ValueError("circunferências coincidentes")
    if d > a.r + b.r + EPS or d < abs(a.r - b.r) - EPS or d < EPS:
        return []
    along = (a.r**2 - b.r**2 + d**2) / (2 * d)
    h2 = a.r**2 - along**2
    mx, my = a.cx + along * dx / d, a.cy + along * dy / d
    if h2 <= EPS * max(1.0, a.r**2):
        return [(mx, my)]
    h = math.sqrt(h2)
    return [(mx - h * dy / d, my + h * dx / d), (mx + h * dy / d, my - h * dx / d)]


def circulo_reta(c: Circulo, p: Ponto, q: Ponto) -> list[Ponto]:
    """Interseções da circunferência com a reta infinita por p e q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    if dx == 0 and dy == 0:
        raise ValueError("reta definida por pontos iguais")
    fx, fy = p[0] - c.cx, p[1] - c.cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    cc = fx * fx + fy * fy - c.r**2
    disc = b * b - 4 * a * cc
    if disc < -EPS * max(1.0, abs(b * b)):
        return []
    if abs(disc) <= EPS * max(1.0, abs(b * b)):
        t = -b / (2 * a)
        return [(p[0] + t * dx, p[1] + t * dy)]
    raiz = math.sqrt(disc)
    return [
        (p[0] + t * dx, p[1] + t * dy) for t in sorted(((-b - raiz) / (2 * a), (-b + raiz) / (2 * a)))
    ]


def circulo_segmento(c: Circulo, p: Ponto, q: Ponto) -> list[Ponto]:
    """Interseções com o segmento fechado pq."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    d2 = dx * dx + dy * dy
    resultado = []
    for x, y in circulo_reta(c, p, q):
        t = ((x - p[0]) * dx + (y - p[1]) * dy) / d2
        if -EPS <= t <= 1 + EPS:
            resultado.append((x, y))
    return resultado


def tangentes_de_ponto(c: Circulo, p: Ponto) -> list[Ponto]:
    """Pontos de tangência das retas tangentes ao círculo traçadas a partir de p."""
    d = math.hypot(p[0] - c.cx, p[1] - c.cy)
    if d < c.r - EPS:
        return []
    if abs(d - c.r) <= EPS:
        return [p]
    # circunferência de diâmetro (centro, p) cruza o círculo nos pontos de tangência
    mx, my = (p[0] + c.cx) / 2, (p[1] + c.cy) / 2
    return circulo_circulo(c, Circulo(mx, my, d / 2))
