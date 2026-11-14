"""Classe NumeroComplexo."""
from __future__ import annotations

import math


class NumeroComplexo:
    def __init__(self, real: float = 0.0, imag: float = 0.0) -> None:
        self.real = float(real)
        self.imag = float(imag)

    @staticmethod
    def _c(o: object) -> "NumeroComplexo":
        if isinstance(o, NumeroComplexo):
            return o
        if isinstance(o, (int, float)):
            return NumeroComplexo(o, 0)
        raise TypeError("operando inválido")

    @classmethod
    def polar(cls, modulo: float, angulo: float) -> "NumeroComplexo":
        return cls(modulo * math.cos(angulo), modulo * math.sin(angulo))

    def __add__(self, o: object) -> "NumeroComplexo":
        o = self._c(o)
        return NumeroComplexo(self.real + o.real, self.imag + o.imag)

    __radd__ = __add__

    def __sub__(self, o: object) -> "NumeroComplexo":
        o = self._c(o)
        return NumeroComplexo(self.real - o.real, self.imag - o.imag)

    def __mul__(self, o: object) -> "NumeroComplexo":
        o = self._c(o)
        return NumeroComplexo(self.real * o.real - self.imag * o.imag,
                              self.real * o.imag + self.imag * o.real)

    __rmul__ = __mul__

    def __truediv__(self, o: object) -> "NumeroComplexo":
        o = self._c(o)
        d = o.real ** 2 + o.imag ** 2
        if d == 0:
            raise ZeroDivisionError("divisão por zero complexo")
        n = self * o.conjugado()
        return NumeroComplexo(n.real / d, n.imag / d)

    def __neg__(self) -> "NumeroComplexo":
        return NumeroComplexo(-self.real, -self.imag)

    def conjugado(self) -> "NumeroComplexo":
        return NumeroComplexo(self.real, -self.imag)

    def modulo(self) -> float:
        return math.hypot(self.real, self.imag)

    def argumento(self) -> float:
        return math.atan2(self.imag, self.real)

    def potencia(self, n: int) -> "NumeroComplexo":
        """Potência inteira por exponenciação rápida."""
        if n < 0:
            return NumeroComplexo(1) / self.potencia(-n)
        r, b = NumeroComplexo(1), self
        while n:
            if n & 1:
                r = r * b
            b = b * b
            n >>= 1
        return r

    def __eq__(self, o: object) -> bool:
        if isinstance(o, (NumeroComplexo, int, float)):
            o = self._c(o)
            return self.real == o.real and self.imag == o.imag
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.real, self.imag))

    def __repr__(self) -> str:
        return f"NumeroComplexo({self.real}, {self.imag})"

    def __str__(self) -> str:
        sinal = "-" if self.imag < 0 else "+"
        return f"{self.real:g} {sinal} {abs(self.imag):g}i"
