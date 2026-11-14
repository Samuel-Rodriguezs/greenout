"""Naive Bayes gaussiano para atributos contínuos."""
from __future__ import annotations

import math
from collections import defaultdict


class NaiveBayesGaussiano:
    def __init__(self, suavizacao: float = 1e-9) -> None:
        self.suavizacao = suavizacao
        self.classes: list = []
        self.priori: dict = {}
        self.medias: dict = {}
        self.variancias: dict = {}

    def treinar(self, X: list[list[float]], y: list) -> "NaiveBayesGaussiano":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        grupos = defaultdict(list)
        for x, r in zip(X, y):
            grupos[r].append(x)
        self.classes = sorted(grupos, key=str)
        for c in self.classes:
            linhas = grupos[c]
            self.priori[c] = len(linhas) / len(X)
            cols = list(zip(*linhas))
            self.medias[c] = [sum(col) / len(col) for col in cols]
            self.variancias[c] = [
                sum((v - m) ** 2 for v in col) / len(col) + self.suavizacao
                for col, m in zip(cols, self.medias[c])
            ]
        return self

    def log_posteriori(self, x: list[float]) -> dict:
        saida = {}
        for c in self.classes:
            lp = math.log(self.priori[c])
            for v, m, var in zip(x, self.medias[c], self.variancias[c]):
                lp += -0.5 * math.log(2 * math.pi * var) - (v - m) ** 2 / (2 * var)
            saida[c] = lp
        return saida

    def prever_um(self, x: list[float]):
        lp = self.log_posteriori(x)
        return max(self.classes, key=lambda c: lp[c])

    def prever(self, X: list[list[float]]) -> list:
        return [self.prever_um(x) for x in X]

    def proba(self, x: list[float]) -> dict:
        lp = self.log_posteriori(x)
        m = max(lp.values())
        exp = {c: math.exp(v - m) for c, v in lp.items()}
        s = sum(exp.values())
        return {c: v / s for c, v in exp.items()}
