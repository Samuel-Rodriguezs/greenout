"""Normalizador (min-max) e padronizador (z-score) com fit/transform."""
from __future__ import annotations

import math


class Padronizador:
    """z-score por coluna: (x - média) / desvio populacional."""

    def __init__(self) -> None:
        self.medias: list[float] = []
        self.desvios: list[float] = []

    def ajustar(self, X: list[list[float]]) -> "Padronizador":
        if not X:
            raise ValueError("X vazio")
        cols = list(zip(*X))
        self.medias = [sum(c) / len(c) for c in cols]
        self.desvios = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) for c, m in zip(cols, self.medias)]
        return self

    def transformar(self, X: list[list[float]]) -> list[list[float]]:
        if not self.medias:
            raise RuntimeError("chame ajustar antes")
        return [[(v - m) / d if d else 0.0 for v, m, d in zip(x, self.medias, self.desvios)] for x in X]

    def ajustar_transformar(self, X):
        return self.ajustar(X).transformar(X)

    def inverter(self, X: list[list[float]]) -> list[list[float]]:
        return [[v * d + m for v, m, d in zip(x, self.medias, self.desvios)] for x in X]


class Normalizador:
    """Min-max para o intervalo [minimo, maximo] (padrão [0, 1])."""

    def __init__(self, minimo: float = 0.0, maximo: float = 1.0) -> None:
        if minimo >= maximo:
            raise ValueError("minimo deve ser menor que maximo")
        self.minimo, self.maximo = minimo, maximo
        self.mins: list[float] = []
        self.maxs: list[float] = []

    def ajustar(self, X: list[list[float]]) -> "Normalizador":
        if not X:
            raise ValueError("X vazio")
        cols = list(zip(*X))
        self.mins = [min(c) for c in cols]
        self.maxs = [max(c) for c in cols]
        return self

    def transformar(self, X: list[list[float]]) -> list[list[float]]:
        if not self.mins:
            raise RuntimeError("chame ajustar antes")
        esc = self.maximo - self.minimo
        return [[self.minimo + (v - lo) / (hi - lo) * esc if hi > lo else self.minimo
                 for v, lo, hi in zip(x, self.mins, self.maxs)] for x in X]

    def ajustar_transformar(self, X):
        return self.ajustar(X).transformar(X)

    def inverter(self, X: list[list[float]]) -> list[list[float]]:
        esc = self.maximo - self.minimo
        return [[lo + (v - self.minimo) / esc * (hi - lo) for v, lo, hi in zip(x, self.mins, self.maxs)]
                for x in X]
