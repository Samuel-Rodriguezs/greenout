"""SVM linear (hinge loss + regularização L2) treinada por SGD, estilo Pegasos."""
from __future__ import annotations

import random


class SVMLinear:
    def __init__(self, lambda_: float = 0.01, epocas: int = 50, seed: int = 0) -> None:
        self.lambda_ = lambda_
        self.epocas = epocas
        self.seed = seed
        self.pesos: list[float] = []
        self.vies = 0.0

    def decisao(self, x: list[float]) -> float:
        return self.vies + sum(w * v for w, v in zip(self.pesos, x))

    def treinar(self, X: list[list[float]], y: list[int]) -> "SVMLinear":
        """y em {-1, +1}."""
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        if any(r not in (-1, 1) for r in y):
            raise ValueError("rótulos devem ser -1 ou +1")
        rng = random.Random(self.seed)
        self.pesos = [0.0] * len(X[0])
        self.vies = 0.0
        t = 0
        idx = list(range(len(X)))
        for _ in range(self.epocas):
            rng.shuffle(idx)
            for i in idx:
                t += 1
                eta = 1.0 / (self.lambda_ * t)
                margem = y[i] * self.decisao(X[i])
                self.pesos = [(1 - eta * self.lambda_) * w for w in self.pesos]
                if margem < 1:
                    self.pesos = [w + eta * y[i] * v for w, v in zip(self.pesos, X[i])]
                    self.vies += eta * y[i] * 0.1
        return self

    def prever(self, X: list[list[float]]) -> list[int]:
        return [1 if self.decisao(x) >= 0 else -1 for x in X]

    def margens(self, X: list[list[float]], y: list[int]) -> list[float]:
        return [yi * self.decisao(x) for x, yi in zip(X, y)]
