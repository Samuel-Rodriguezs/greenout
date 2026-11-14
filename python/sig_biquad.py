"""Filtros IIR de 1a ordem e biquad (Direct Form I), receitas do Audio EQ Cookbook."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Biquad:
    """y[n] = b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2] (a0 = 1)."""

    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    _x1: float = 0.0
    _x2: float = 0.0
    _y1: float = 0.0
    _y2: float = 0.0

    def processar(self, x: float) -> float:
        y = self.b0 * x + self.b1 * self._x1 + self.b2 * self._x2 - self.a1 * self._y1 - self.a2 * self._y2
        self._x2, self._x1 = self._x1, x
        self._y2, self._y1 = self._y1, y
        return y

    def filtrar(self, x: list[float]) -> list[float]:
        return [self.processar(v) for v in x]

    def resetar(self) -> None:
        self._x1 = self._x2 = self._y1 = self._y2 = 0.0

    def ganho(self, freq: float, taxa: float) -> float:
        """|H(e^{jw})| na frequência dada."""
        w = 2 * math.pi * freq / taxa
        num = complex(self.b0, 0) + self.b1 * complex(math.cos(w), -math.sin(w)) \
            + self.b2 * complex(math.cos(2 * w), -math.sin(2 * w))
        den = 1 + self.a1 * complex(math.cos(w), -math.sin(w)) \
            + self.a2 * complex(math.cos(2 * w), -math.sin(2 * w))
        return abs(num / den)


def _validar(freq: float, taxa: float, q: float = 1.0) -> None:
    if taxa <= 0 or not 0 < freq < taxa / 2:
        raise ValueError("freq deve estar entre 0 e taxa/2")
    if q <= 0:
        raise ValueError("q deve ser positivo")


def passa_baixa_1a_ordem(freq: float, taxa: float) -> Biquad:
    """Passa-baixa de 1a ordem pela transformação bilinear."""
    _validar(freq, taxa)
    k = math.tan(math.pi * freq / taxa)
    d = 1 + k
    return Biquad(k / d, k / d, 0.0, (k - 1) / d, 0.0)


def passa_alta_1a_ordem(freq: float, taxa: float) -> Biquad:
    _validar(freq, taxa)
    k = math.tan(math.pi * freq / taxa)
    d = 1 + k
    return Biquad(1 / d, -1 / d, 0.0, (k - 1) / d, 0.0)


def _cookbook(freq: float, taxa: float, q: float) -> tuple[float, float, float]:
    _validar(freq, taxa, q)
    w0 = 2 * math.pi * freq / taxa
    return math.cos(w0), math.sin(w0), math.sin(w0) / (2 * q)


def passa_baixa(freq: float, taxa: float, q: float = 1 / math.sqrt(2)) -> Biquad:
    c, _, alfa = _cookbook(freq, taxa, q)
    a0 = 1 + alfa
    return Biquad((1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0, -2 * c / a0, (1 - alfa) / a0)


def passa_alta(freq: float, taxa: float, q: float = 1 / math.sqrt(2)) -> Biquad:
    c, _, alfa = _cookbook(freq, taxa, q)
    a0 = 1 + alfa
    return Biquad((1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0, -2 * c / a0, (1 - alfa) / a0)


def passa_banda(freq: float, taxa: float, q: float = 1.0) -> Biquad:
    """Passa-banda com ganho de pico 1 na frequência central."""
    c, _, alfa = _cookbook(freq, taxa, q)
    a0 = 1 + alfa
    return Biquad(alfa / a0, 0.0, -alfa / a0, -2 * c / a0, (1 - alfa) / a0)


def rejeita_faixa(freq: float, taxa: float, q: float = 1.0) -> Biquad:
    """Notch."""
    c, _, alfa = _cookbook(freq, taxa, q)
    a0 = 1 + alfa
    return Biquad(1 / a0, -2 * c / a0, 1 / a0, -2 * c / a0, (1 - alfa) / a0)
