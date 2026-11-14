"""Integração de Verlet com restrições de distância (cordas, tecidos, corpos rígidos)."""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass
class Ponto:
    x: float
    y: float
    ox: float = 0.0  # posição anterior
    oy: float = 0.0
    fixo: bool = False

    def __post_init__(self) -> None:
        self.ox, self.oy = self.x, self.y


@dataclass
class Restricao:
    a: int
    b: int
    comprimento: float
    rigidez: float = 1.0


class SistemaVerlet:
    def __init__(self, gravidade: tuple[float, float] = (0.0, 9.8), amortecimento: float = 1.0) -> None:
        self.pontos: list[Ponto] = []
        self.restricoes: list[Restricao] = []
        self.gravidade = gravidade
        self.amortecimento = amortecimento

    def adicionar_ponto(self, x: float, y: float, fixo: bool = False) -> int:
        self.pontos.append(Ponto(x, y, fixo=fixo))
        return len(self.pontos) - 1

    def ligar(self, a: int, b: int, comprimento: float | None = None, rigidez: float = 1.0) -> None:
        pa, pb = self.pontos[a], self.pontos[b]
        if comprimento is None:
            comprimento = hypot(pa.x - pb.x, pa.y - pb.y)
        self.restricoes.append(Restricao(a, b, comprimento, rigidez))

    def passo(self, dt: float, iteracoes: int = 8) -> None:
        dt2 = dt * dt
        gx, gy = self.gravidade
        for p in self.pontos:
            if p.fixo:
                continue
            vx = (p.x - p.ox) * self.amortecimento
            vy = (p.y - p.oy) * self.amortecimento
            p.ox, p.oy = p.x, p.y
            p.x += vx + gx * dt2
            p.y += vy + gy * dt2
        for _ in range(iteracoes):
            for r in self.restricoes:
                self._relaxar(r)

    def _relaxar(self, r: Restricao) -> None:
        a, b = self.pontos[r.a], self.pontos[r.b]
        dx, dy = b.x - a.x, b.y - a.y
        dist = hypot(dx, dy)
        if dist == 0:
            return
        erro = (dist - r.comprimento) / dist * r.rigidez
        if a.fixo and b.fixo:
            return
        if a.fixo:
            b.x -= dx * erro
            b.y -= dy * erro
        elif b.fixo:
            a.x += dx * erro
            a.y += dy * erro
        else:
            a.x += dx * erro / 2
            a.y += dy * erro / 2
            b.x -= dx * erro / 2
            b.y -= dy * erro / 2

    def velocidade(self, i: int) -> tuple[float, float]:
        """Velocidade implícita por passo (posição atual - anterior)."""
        p = self.pontos[i]
        return (p.x - p.ox, p.y - p.oy)
