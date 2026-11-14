"""Vetores 2D e 3D imutáveis com produto escalar, vetorial e projeção."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vetor2:
    x: float
    y: float

    def __add__(self, o: Vetor2) -> Vetor2:
        return Vetor2(self.x + o.x, self.y + o.y)

    def __sub__(self, o: Vetor2) -> Vetor2:
        return Vetor2(self.x - o.x, self.y - o.y)

    def __mul__(self, k: float) -> Vetor2:
        return Vetor2(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __neg__(self) -> Vetor2:
        return Vetor2(-self.x, -self.y)

    def dot(self, o: Vetor2) -> float:
        return self.x * o.x + self.y * o.y

    def cross(self, o: Vetor2) -> float:
        """Componente z do produto vetorial."""
        return self.x * o.y - self.y * o.x

    def norma(self) -> float:
        return math.hypot(self.x, self.y)

    def normalizado(self) -> Vetor2:
        n = self.norma()
        if n == 0:
            raise ValueError("vetor nulo não pode ser normalizado")
        return Vetor2(self.x / n, self.y / n)

    def perpendicular(self) -> Vetor2:
        return Vetor2(-self.y, self.x)

    def angulo(self) -> float:
        return math.atan2(self.y, self.x)

    def angulo_com(self, o: Vetor2) -> float:
        return abs(math.atan2(self.cross(o), self.dot(o)))

    def projetar_em(self, o: Vetor2) -> Vetor2:
        d = o.dot(o)
        if d == 0:
            raise ValueError("não se projeta sobre vetor nulo")
        return o * (self.dot(o) / d)


@dataclass(frozen=True)
class Vetor3:
    x: float
    y: float
    z: float

    def __add__(self, o: Vetor3) -> Vetor3:
        return Vetor3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: Vetor3) -> Vetor3:
        return Vetor3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, k: float) -> Vetor3:
        return Vetor3(self.x * k, self.y * k, self.z * k)

    __rmul__ = __mul__

    def dot(self, o: Vetor3) -> float:
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o: Vetor3) -> Vetor3:
        return Vetor3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def norma(self) -> float:
        return math.sqrt(self.dot(self))

    def normalizado(self) -> Vetor3:
        n = self.norma()
        if n == 0:
            raise ValueError("vetor nulo não pode ser normalizado")
        return Vetor3(self.x / n, self.y / n, self.z / n)

    def produto_misto(self, b: Vetor3, c: Vetor3) -> float:
        return self.dot(b.cross(c))
