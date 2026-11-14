"""Colisão 2D: AABB, círculo-círculo, círculo-AABB e resolução por sobreposição mínima.

Todas as funções `mtv_*` devolvem o vetor (dx, dy) que, somado à posição do
primeiro corpo, o separa do segundo com o menor deslocamento; `None` se não há
sobreposição (contato apenas tangente não conta).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot

Vetor = tuple[float, float]


@dataclass
class AABB:
    x: float  # canto superior esquerdo
    y: float
    w: float
    h: float

    @property
    def direita(self) -> float:
        return self.x + self.w

    @property
    def baixo(self) -> float:
        return self.y + self.h

    @property
    def centro(self) -> Vetor:
        return (self.x + self.w / 2, self.y + self.h / 2)


@dataclass
class Circulo:
    x: float  # centro
    y: float
    r: float


def aabb_aabb(a: AABB, b: AABB) -> bool:
    return a.x < b.direita and b.x < a.direita and a.y < b.baixo and b.y < a.baixo


def mtv_aabb(a: AABB, b: AABB) -> Vetor | None:
    ox = min(a.direita, b.direita) - max(a.x, b.x)
    oy = min(a.baixo, b.baixo) - max(a.y, b.y)
    if ox <= 0 or oy <= 0:
        return None
    (ax, ay), (bx, by) = a.centro, b.centro
    if ox < oy:
        return (-ox if ax < bx else ox, 0.0)
    return (0.0, -oy if ay < by else oy)


def mtv_circulos(a: Circulo, b: Circulo) -> Vetor | None:
    dx, dy = a.x - b.x, a.y - b.y
    dist = hypot(dx, dy)
    soma = a.r + b.r
    if dist >= soma:
        return None
    if dist == 0:
        return (soma, 0.0)
    pen = soma - dist
    return (dx / dist * pen, dy / dist * pen)


def mtv_circulo_aabb(c: Circulo, caixa: AABB) -> Vetor | None:
    px = min(max(c.x, caixa.x), caixa.direita)
    py = min(max(c.y, caixa.y), caixa.baixo)
    dx, dy = c.x - px, c.y - py
    dist = hypot(dx, dy)
    if dist > 0:
        if dist >= c.r:
            return None
        pen = c.r - dist
        return (dx / dist * pen, dy / dist * pen)
    # centro dentro (ou sobre a borda) da caixa: sai pelo lado mais próximo
    opcoes = [
        (c.x - caixa.x + c.r, (-1.0, 0.0)),
        (caixa.direita - c.x + c.r, (1.0, 0.0)),
        (c.y - caixa.y + c.r, (0.0, -1.0)),
        (caixa.baixo - c.y + c.r, (0.0, 1.0)),
    ]
    dist_min, (ux, uy) = min(opcoes, key=lambda o: o[0])
    return (ux * dist_min, uy * dist_min)


def resolver(a: AABB, b: AABB, massa_a: float = 1.0, massa_b: float = 1.0) -> bool:
    """Separa dois AABBs movendo-os conforme a razão inversa das massas.

    Massa infinita (`float('inf')`) torna o corpo imóvel. Devolve se houve colisão.
    """
    mtv = mtv_aabb(a, b)
    if mtv is None:
        return False
    inv_a = 0.0 if massa_a == float("inf") else 1.0 / massa_a
    inv_b = 0.0 if massa_b == float("inf") else 1.0 / massa_b
    total = inv_a + inv_b
    if total == 0:
        return True
    fa, fb = inv_a / total, inv_b / total
    a.x += mtv[0] * fa
    a.y += mtv[1] * fa
    b.x -= mtv[0] * fb
    b.y -= mtv[1] * fb
    return True
