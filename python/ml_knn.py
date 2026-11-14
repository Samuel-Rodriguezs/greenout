"""k-vizinhos mais próximos (classificação e regressão) do zero."""
from __future__ import annotations

import math
from collections import Counter


def distancia_euclidiana(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def distancia_manhattan(a: list[float], b: list[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


class KNN:
    def __init__(self, k: int = 3, distancia=distancia_euclidiana) -> None:
        if k < 1:
            raise ValueError("k deve ser >= 1")
        self.k = k
        self.distancia = distancia
        self.X: list[list[float]] = []
        self.y: list = []

    def treinar(self, X: list[list[float]], y: list) -> "KNN":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        self.X, self.y = X, y
        return self

    def vizinhos(self, x: list[float]) -> list[tuple[float, object]]:
        pares = sorted(((self.distancia(x, xi), i) for i, xi in enumerate(self.X)))
        return [(d, self.y[i]) for d, i in pares[: self.k]]

    def classificar(self, x: list[float]):
        votos = Counter(rotulo for _, rotulo in self.vizinhos(x))
        melhor = max(votos.values())
        # desempate: o rótulo do vizinho mais próximo entre os empatados
        for _, rotulo in self.vizinhos(x):
            if votos[rotulo] == melhor:
                return rotulo

    def regredir(self, x: list[float]) -> float:
        viz = self.vizinhos(x)
        return sum(r for _, r in viz) / len(viz)

    def prever(self, X: list[list[float]]) -> list:
        return [self.classificar(x) for x in X]
