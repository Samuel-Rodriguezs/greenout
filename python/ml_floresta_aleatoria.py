"""Floresta aleatória simples: bagging de árvores com subamostra de atributos."""
from __future__ import annotations

import random
from collections import Counter

from ml_arvore_decisao import ArvoreDecisao


class FlorestaAleatoria:
    def __init__(self, n_arvores: int = 15, profundidade_max: int | None = 5,
                 n_atributos: int | None = None, seed: int = 0) -> None:
        if n_arvores < 1:
            raise ValueError("n_arvores deve ser >= 1")
        self.n_arvores = n_arvores
        self.profundidade_max = profundidade_max
        self.n_atributos = n_atributos
        self.seed = seed
        self.arvores: list[ArvoreDecisao] = []

    def treinar(self, X: list[list[float]], y: list) -> "FlorestaAleatoria":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        rng = random.Random(self.seed)
        d = len(X[0])
        k = self.n_atributos or max(1, round(d ** 0.5))
        self.arvores = []
        for _ in range(self.n_arvores):
            idx = [rng.randrange(len(X)) for _ in range(len(X))]
            cols = rng.sample(range(d), min(k, d))
            arv = ArvoreDecisao(profundidade_max=self.profundidade_max, atributos=cols)
            arv.treinar([X[i] for i in idx], [y[i] for i in idx])
            self.arvores.append(arv)
        return self

    def prever_um(self, x: list[float]):
        votos = Counter(a.prever_um(x) for a in self.arvores)
        melhor = max(votos.values())
        return sorted((r for r, c in votos.items() if c == melhor), key=str)[0]

    def prever(self, X: list[list[float]]) -> list:
        return [self.prever_um(x) for x in X]
