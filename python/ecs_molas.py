"""Molas amortecidas (lei de Hooke) entre partículas 1D/2D, integradas por Euler semi-implícito."""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass
class Corpo:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    massa: float = 1.0
    fixo: bool = False


@dataclass
class Mola:
    a: Corpo
    b: Corpo
    repouso: float
    k: float
    amortecimento: float = 0.0

    def forca_em_a(self) -> tuple[float, float]:
        """Força sobre `a` (a força sobre `b` é a oposta)."""
        dx, dy = self.b.x - self.a.x, self.b.y - self.a.y
        dist = hypot(dx, dy)
        if dist == 0:
            return (0.0, 0.0)
        ux, uy = dx / dist, dy / dist
        # estica (dist > repouso) => puxa a em direção a b
        f = self.k * (dist - self.repouso)
        vrel = (self.b.vx - self.a.vx) * ux + (self.b.vy - self.a.vy) * uy
        f += self.amortecimento * vrel
        return (f * ux, f * uy)


def passo(corpos: list[Corpo], molas: list[Mola], dt: float, gravidade: tuple[float, float] = (0.0, 0.0)) -> None:
    forcas = {id(c): [c.massa * gravidade[0], c.massa * gravidade[1]] for c in corpos}
    for m in molas:
        fx, fy = m.forca_em_a()
        for c, s in ((m.a, 1), (m.b, -1)):
            f = forcas.setdefault(id(c), [0.0, 0.0])
            f[0] += s * fx
            f[1] += s * fy
    for c in corpos:
        if c.fixo:
            continue
        fx, fy = forcas[id(c)]
        c.vx += fx / c.massa * dt
        c.vy += fy / c.massa * dt
        c.x += c.vx * dt
        c.y += c.vy * dt


def energia(corpos: list[Corpo], molas: list[Mola]) -> float:
    """Energia mecânica (cinética + elástica), sem gravidade."""
    cin = sum(0.5 * c.massa * (c.vx ** 2 + c.vy ** 2) for c in corpos if not c.fixo)
    el = sum(0.5 * m.k * (hypot(m.b.x - m.a.x, m.b.y - m.a.y) - m.repouso) ** 2 for m in molas)
    return cin + el
