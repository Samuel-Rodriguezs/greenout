"""Classe Fracao com aritmética racional exata."""
from __future__ import annotations

from math import gcd


class Fracao:
    def __init__(self, numerador: int, denominador: int = 1) -> None:
        if denominador == 0:
            raise ZeroDivisionError("denominador zero")
        if denominador < 0:
            numerador, denominador = -numerador, -denominador
        g = gcd(numerador, denominador) or 1
        self.num = numerador // g
        self.den = denominador // g

    @staticmethod
    def _coagir(o: object) -> "Fracao":
        if isinstance(o, Fracao):
            return o
        if isinstance(o, int):
            return Fracao(o)
        raise TypeError("operando inválido")

    def __add__(self, o: object) -> "Fracao":
        o = self._coagir(o)
        return Fracao(self.num * o.den + o.num * self.den, self.den * o.den)

    __radd__ = __add__

    def __sub__(self, o: object) -> "Fracao":
        o = self._coagir(o)
        return Fracao(self.num * o.den - o.num * self.den, self.den * o.den)

    def __rsub__(self, o: object) -> "Fracao":
        return self._coagir(o) - self

    def __mul__(self, o: object) -> "Fracao":
        o = self._coagir(o)
        return Fracao(self.num * o.num, self.den * o.den)

    __rmul__ = __mul__

    def __truediv__(self, o: object) -> "Fracao":
        o = self._coagir(o)
        if o.num == 0:
            raise ZeroDivisionError("divisão por zero")
        return Fracao(self.num * o.den, self.den * o.num)

    def __neg__(self) -> "Fracao":
        return Fracao(-self.num, self.den)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, (Fracao, int)):
            o = self._coagir(o)
            return self.num == o.num and self.den == o.den
        return NotImplemented

    def __lt__(self, o: object) -> bool:
        o = self._coagir(o)
        return self.num * o.den < o.num * self.den

    def __le__(self, o: object) -> bool:
        return self == o or self < o

    def __hash__(self) -> int:
        return hash((self.num, self.den))

    def __float__(self) -> float:
        return self.num / self.den

    def __repr__(self) -> str:
        return f"Fracao({self.num}, {self.den})"

    def __str__(self) -> str:
        return str(self.num) if self.den == 1 else f"{self.num}/{self.den}"
