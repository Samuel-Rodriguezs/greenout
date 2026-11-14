"""Perceptron simples (classificador binário linear) do zero."""
from __future__ import annotations

import random


class Perceptron:
    """Perceptron com regra de aprendizado clássica; rótulos em {0, 1}."""

    def __init__(self, taxa: float = 0.1, epocas: int = 100, seed: int = 0) -> None:
        self.taxa = taxa
        self.epocas = epocas
        self.seed = seed
        self.pesos: list[float] = []
        self.vies: float = 0.0
        self.epocas_usadas: int = 0

    def prever_um(self, x: list[float]) -> int:
        soma = self.vies + sum(w * v for w, v in zip(self.pesos, x))
        return 1 if soma >= 0 else 0

    def prever(self, X: list[list[float]]) -> list[int]:
        return [self.prever_um(x) for x in X]

    def treinar(self, X: list[list[float]], y: list[int]) -> "Perceptron":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        rng = random.Random(self.seed)
        self.pesos = [0.0] * len(X[0])
        self.vies = 0.0
        indices = list(range(len(X)))
        for epoca in range(1, self.epocas + 1):
            rng.shuffle(indices)
            erros = 0
            for i in indices:
                erro = y[i] - self.prever_um(X[i])
                if erro:
                    erros += 1
                    for j, v in enumerate(X[i]):
                        self.pesos[j] += self.taxa * erro * v
                    self.vies += self.taxa * erro
            self.epocas_usadas = epoca
            if erros == 0:
                break
        return self


def acuracia(y: list[int], previsto: list[int]) -> float:
    return sum(a == b for a, b in zip(y, previsto)) / len(y)
