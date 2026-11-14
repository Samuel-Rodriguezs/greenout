"""Regressão logística binária por gradiente descendente em lote."""
from __future__ import annotations

import math


def sigmoide(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


class RegressaoLogistica:
    def __init__(self, taxa: float = 0.5, iteracoes: int = 1000, l2: float = 0.0) -> None:
        self.taxa = taxa
        self.iteracoes = iteracoes
        self.l2 = l2
        self.pesos: list[float] = []
        self.vies = 0.0
        self.historico_perda: list[float] = []

    def proba_um(self, x: list[float]) -> float:
        return sigmoide(self.vies + sum(w * v for w, v in zip(self.pesos, x)))

    def proba(self, X: list[list[float]]) -> list[float]:
        return [self.proba_um(x) for x in X]

    def prever(self, X: list[list[float]], limiar: float = 0.5) -> list[int]:
        return [1 if p >= limiar else 0 for p in self.proba(X)]

    def perda(self, X: list[list[float]], y: list[int]) -> float:
        eps = 1e-12
        total = 0.0
        for x, alvo in zip(X, y):
            p = min(max(self.proba_um(x), eps), 1 - eps)
            total -= alvo * math.log(p) + (1 - alvo) * math.log(1 - p)
        return total / len(X)

    def treinar(self, X: list[list[float]], y: list[int]) -> "RegressaoLogistica":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        n, d = len(X), len(X[0])
        self.pesos = [0.0] * d
        self.vies = 0.0
        self.historico_perda = []
        for _ in range(self.iteracoes):
            gp = [0.0] * d
            gb = 0.0
            for x, alvo in zip(X, y):
                erro = self.proba_um(x) - alvo
                for j in range(d):
                    gp[j] += erro * x[j]
                gb += erro
            for j in range(d):
                self.pesos[j] -= self.taxa * (gp[j] / n + self.l2 * self.pesos[j])
            self.vies -= self.taxa * gb / n
            self.historico_perda.append(self.perda(X, y))
        return self
