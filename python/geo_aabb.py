"""Caixas delimitadoras alinhadas aos eixos (AABB) em 2D."""
from __future__ import annotations

from dataclasses import dataclass

Ponto = tuple[float, float]


@dataclass(frozen=True)
class AABB:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def __post_init__(self) -> None:
        if self.xmin > self.xmax or self.ymin > self.ymax:
            raise ValueError("limites invertidos")

    @classmethod
    def de_pontos(cls, pontos: list[Ponto]) -> AABB:
        if not pontos:
            raise ValueError("sem pontos")
        xs = [p[0] for p in pontos]
        ys = [p[1] for p in pontos]
        return cls(min(xs), min(ys), max(xs), max(ys))

    @property
    def largura(self) -> float:
        return self.xmax - self.xmin

    @property
    def altura(self) -> float:
        return self.ymax - self.ymin

    @property
    def area(self) -> float:
        return self.largura * self.altura

    @property
    def centro(self) -> Ponto:
        return ((self.xmin + self.xmax) / 2, (self.ymin + self.ymax) / 2)

    def contem_ponto(self, p: Ponto) -> bool:
        return self.xmin <= p[0] <= self.xmax and self.ymin <= p[1] <= self.ymax

    def contem(self, o: AABB) -> bool:
        return (
            self.xmin <= o.xmin and self.ymin <= o.ymin and o.xmax <= self.xmax and o.ymax <= self.ymax
        )

    def intersecta(self, o: AABB) -> bool:
        """True se as caixas fechadas compartilham ao menos um ponto (encostar conta)."""
        return (
            self.xmin <= o.xmax and o.xmin <= self.xmax and self.ymin <= o.ymax and o.ymin <= self.ymax
        )

    def intersecao(self, o: AABB) -> AABB | None:
        if not self.intersecta(o):
            return None
        return AABB(max(self.xmin, o.xmin), max(self.ymin, o.ymin), min(self.xmax, o.xmax), min(self.ymax, o.ymax))

    def uniao(self, o: AABB) -> AABB:
        return AABB(min(self.xmin, o.xmin), min(self.ymin, o.ymin), max(self.xmax, o.xmax), max(self.ymax, o.ymax))

    def expandir(self, margem: float) -> AABB:
        return AABB(self.xmin - margem, self.ymin - margem, self.xmax + margem, self.ymax + margem)

    def distancia_ao_ponto(self, p: Ponto) -> float:
        dx = max(self.xmin - p[0], 0, p[0] - self.xmax)
        dy = max(self.ymin - p[1], 0, p[1] - self.ymax)
        return (dx * dx + dy * dy) ** 0.5

    def intersecta_segmento(self, a: Ponto, b: Ponto) -> bool:
        """Slab method (Liang-Barsky) para o segmento ab."""
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in ((-dx, a[0] - self.xmin), (dx, self.xmax - a[0]),
                     (-dy, a[1] - self.ymin), (dy, self.ymax - a[1])):
            if p == 0:
                if q < 0:
                    return False
                continue
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
        return True
