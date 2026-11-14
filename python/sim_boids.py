"""Boids simplificado: separação, alinhamento e coesão em 2D."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class Boid:
    x: float
    y: float
    vx: float
    vy: float


class Bando:
    def __init__(self, n: int, largura: float, altura: float, rng: random.Random | None = None,
                 raio_visao: float = 10.0, raio_separacao: float = 2.0, vmax: float = 2.0) -> None:
        self.rng = rng or random.Random()
        self.largura, self.altura = largura, altura
        self.raio_visao, self.raio_separacao, self.vmax = raio_visao, raio_separacao, vmax
        self.boids = [
            Boid(self.rng.uniform(0, largura), self.rng.uniform(0, altura),
                 self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
            for _ in range(n)
        ]

    def _vizinhos(self, b: Boid) -> list[Boid]:
        return [o for o in self.boids if o is not b and math.hypot(o.x - b.x, o.y - b.y) <= self.raio_visao]

    def passo(self, dt: float = 1.0, w_sep: float = 0.05, w_ali: float = 0.05, w_coe: float = 0.01) -> None:
        novas = []
        for b in self.boids:
            viz = self._vizinhos(b)
            ax = ay = 0.0
            if viz:
                cx = sum(o.x for o in viz) / len(viz)
                cy = sum(o.y for o in viz) / len(viz)
                mx = sum(o.vx for o in viz) / len(viz)
                my = sum(o.vy for o in viz) / len(viz)
                ax += (cx - b.x) * w_coe + (mx - b.vx) * w_ali
                ay += (cy - b.y) * w_coe + (my - b.vy) * w_ali
                for o in viz:
                    if math.hypot(o.x - b.x, o.y - b.y) < self.raio_separacao:
                        ax += (b.x - o.x) * w_sep
                        ay += (b.y - o.y) * w_sep
            vx, vy = b.vx + ax, b.vy + ay
            v = math.hypot(vx, vy)
            if v > self.vmax:
                vx, vy = vx / v * self.vmax, vy / v * self.vmax
            novas.append(Boid((b.x + vx * dt) % self.largura, (b.y + vy * dt) % self.altura, vx, vy))
        self.boids = novas

    def alinhamento(self) -> float:
        """Ordem de alinhamento em [0, 1]: módulo da velocidade média normalizada."""
        vs = [(b.vx, b.vy) for b in self.boids if math.hypot(b.vx, b.vy) > 0]
        if not vs:
            return 0.0
        sx = sum(vx / math.hypot(vx, vy) for vx, vy in vs)
        sy = sum(vy / math.hypot(vx, vy) for vx, vy in vs)
        return math.hypot(sx, sy) / len(vs)
