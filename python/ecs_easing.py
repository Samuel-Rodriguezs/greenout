"""Funções de easing (t em [0, 1] -> [0, 1]) e um tween simples."""
from __future__ import annotations

from math import cos, pi, sin, sqrt
from typing import Callable

Easing = Callable[[float], float]

_C1 = 1.70158
_C3 = _C1 + 1
_C4 = 2 * pi / 3


def linear(t: float) -> float:
    return t


def in_quad(t: float) -> float:
    return t * t


def out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def in_cubic(t: float) -> float:
    return t ** 3


def out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def in_out_cubic(t: float) -> float:
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def in_sine(t: float) -> float:
    return 1 - cos(t * pi / 2)


def out_sine(t: float) -> float:
    return sin(t * pi / 2)


def in_out_sine(t: float) -> float:
    return -(cos(pi * t) - 1) / 2


def in_circ(t: float) -> float:
    return 1 - sqrt(1 - t * t)


def out_circ(t: float) -> float:
    return sqrt(1 - (t - 1) ** 2)


def in_expo(t: float) -> float:
    return 0.0 if t == 0 else 2 ** (10 * t - 10)


def out_expo(t: float) -> float:
    return 1.0 if t == 1 else 1 - 2 ** (-10 * t)


def in_back(t: float) -> float:
    return _C3 * t ** 3 - _C1 * t * t


def out_back(t: float) -> float:
    return 1 + _C3 * (t - 1) ** 3 + _C1 * (t - 1) ** 2


def out_elastic(t: float) -> float:
    if t in (0, 1):
        return float(t)
    return 2 ** (-10 * t) * sin((t * 10 - 0.75) * _C4) + 1


def out_bounce(t: float) -> float:
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


def in_bounce(t: float) -> float:
    return 1 - out_bounce(1 - t)


FUNCOES: dict[str, Easing] = {
    "linear": linear,
    "in_quad": in_quad, "out_quad": out_quad, "in_out_quad": in_out_quad,
    "in_cubic": in_cubic, "out_cubic": out_cubic, "in_out_cubic": in_out_cubic,
    "in_sine": in_sine, "out_sine": out_sine, "in_out_sine": in_out_sine,
    "in_circ": in_circ, "out_circ": out_circ,
    "in_expo": in_expo, "out_expo": out_expo,
    "in_back": in_back, "out_back": out_back,
    "out_elastic": out_elastic,
    "in_bounce": in_bounce, "out_bounce": out_bounce,
}


def interpolar(a: float, b: float, t: float, nome: str = "linear") -> float:
    """Valor entre a e b com a curva `nome`; t é limitado a [0, 1]."""
    try:
        f = FUNCOES[nome]
    except KeyError:
        raise ValueError(f"easing desconhecido: {nome}") from None
    t = min(1.0, max(0.0, t))
    return a + (b - a) * f(t)


class Tween:
    def __init__(self, inicio: float, fim: float, duracao: float, nome: str = "linear") -> None:
        if duracao <= 0:
            raise ValueError("duracao deve ser positiva")
        if nome not in FUNCOES:
            raise ValueError(f"easing desconhecido: {nome}")
        self.inicio, self.fim, self.duracao, self.nome = inicio, fim, duracao, nome
        self.decorrido = 0.0

    def avancar(self, dt: float) -> float:
        self.decorrido = min(self.duracao, self.decorrido + dt)
        return self.valor

    @property
    def valor(self) -> float:
        return interpolar(self.inicio, self.fim, self.decorrido / self.duracao, self.nome)

    @property
    def terminou(self) -> bool:
        return self.decorrido >= self.duracao
