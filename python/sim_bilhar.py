"""Bilhar: colisão elástica entre discos e paredes em 2D."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Bola:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    massa: float = 1.0
    raio: float = 1.0


def colidem(a: Bola, b: Bola) -> bool:
    return math.hypot(a.x - b.x, a.y - b.y) < a.raio + b.raio


def resolver_colisao(a: Bola, b: Bola) -> None:
    """Colisão perfeitamente elástica; conserva momento linear e energia cinética."""
    dx, dy = b.x - a.x, b.y - a.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        raise ValueError("bolas na mesma posição")
    nx, ny = dx / dist, dy / dist
    rel = (a.vx - b.vx) * nx + (a.vy - b.vy) * ny
    if rel <= 0:  # já se afastando
        return
    j = 2 * rel / (1 / a.massa + 1 / b.massa)
    a.vx -= j / a.massa * nx
    a.vy -= j / a.massa * ny
    b.vx += j / b.massa * nx
    b.vy += j / b.massa * ny
    # separa as bolas sobrepostas
    sobra = a.raio + b.raio - dist
    if sobra > 0:
        tot = a.massa + b.massa
        a.x -= nx * sobra * b.massa / tot
        a.y -= ny * sobra * b.massa / tot
        b.x += nx * sobra * a.massa / tot
        b.y += ny * sobra * a.massa / tot


class Mesa:
    def __init__(self, largura: float, altura: float, bolas: list[Bola]) -> None:
        self.largura, self.altura = largura, altura
        self.bolas = bolas

    def passo(self, dt: float, atrito: float = 0.0) -> None:
        for b in self.bolas:
            b.x += b.vx * dt
            b.y += b.vy * dt
            if b.x - b.raio < 0:
                b.x, b.vx = b.raio, abs(b.vx)
            elif b.x + b.raio > self.largura:
                b.x, b.vx = self.largura - b.raio, -abs(b.vx)
            if b.y - b.raio < 0:
                b.y, b.vy = b.raio, abs(b.vy)
            elif b.y + b.raio > self.altura:
                b.y, b.vy = self.altura - b.raio, -abs(b.vy)
            if atrito:
                f = max(0.0, 1 - atrito * dt)
                b.vx *= f
                b.vy *= f
        for i, a in enumerate(self.bolas):
            for b in self.bolas[i + 1:]:
                if colidem(a, b):
                    resolver_colisao(a, b)

    def momento(self) -> tuple[float, float]:
        return (sum(b.massa * b.vx for b in self.bolas), sum(b.massa * b.vy for b in self.bolas))

    def energia(self) -> float:
        return sum(0.5 * b.massa * (b.vx ** 2 + b.vy ** 2) for b in self.bolas)
