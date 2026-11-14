"""Bola quicando em caixa: física discreta com gravidade e perda de energia."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Bola:
    x: float
    y: float
    vx: float
    vy: float
    raio: float = 0.5


class Caixa:
    def __init__(self, largura: float, altura: float, gravidade: float = 9.8,
                 restituicao: float = 0.8) -> None:
        if not 0 <= restituicao <= 1:
            raise ValueError("restituição deve estar em [0, 1]")
        self.largura, self.altura = largura, altura
        self.g = gravidade
        self.e = restituicao
        self.quicadas = 0

    def passo(self, b: Bola, dt: float) -> None:
        """Integração semi-implícita de Euler com colisões nas paredes (y cresce para cima)."""
        b.vy -= self.g * dt
        b.x += b.vx * dt
        b.y += b.vy * dt
        if b.x - b.raio < 0:
            b.x = b.raio + (b.raio - b.x)
            b.vx = -b.vx * self.e
            self.quicadas += 1
        elif b.x + b.raio > self.largura:
            b.x = (self.largura - b.raio) - (b.x + b.raio - self.largura)
            b.vx = -b.vx * self.e
            self.quicadas += 1
        if b.y - b.raio < 0:
            b.y = b.raio + (b.raio - b.y)
            b.vy = -b.vy * self.e
            self.quicadas += 1
        elif b.y + b.raio > self.altura:
            b.y = (self.altura - b.raio) - (b.y + b.raio - self.altura)
            b.vy = -b.vy * self.e
            self.quicadas += 1

    @staticmethod
    def energia(b: Bola, g: float) -> float:
        return 0.5 * (b.vx ** 2 + b.vy ** 2) + g * b.y
