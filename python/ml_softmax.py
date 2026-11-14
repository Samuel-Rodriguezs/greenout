"""Softmax, entropia cruzada e regressão softmax multiclasse."""
from __future__ import annotations

import math


def softmax(z: list[float]) -> list[float]:
    if not z:
        raise ValueError("vetor vazio")
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]


def log_softmax(z: list[float]) -> list[float]:
    m = max(z)
    lse = m + math.log(sum(math.exp(v - m) for v in z))
    return [v - lse for v in z]


def entropia_cruzada(alvo: int, probs: list[float]) -> float:
    """Perda -log p[alvo] para rótulo inteiro."""
    if not 0 <= alvo < len(probs):
        raise ValueError("alvo fora do intervalo")
    return -math.log(max(probs[alvo], 1e-15))


def entropia_cruzada_distribuicao(alvo: list[float], probs: list[float]) -> float:
    if len(alvo) != len(probs):
        raise ValueError("tamanhos diferentes")
    return -sum(a * math.log(max(p, 1e-15)) for a, p in zip(alvo, probs) if a > 0)


class RegressaoSoftmax:
    def __init__(self, n_classes: int, taxa: float = 0.5, iteracoes: int = 200) -> None:
        self.n_classes = n_classes
        self.taxa = taxa
        self.iteracoes = iteracoes
        self.W: list[list[float]] = []
        self.b: list[float] = []
        self.perdas: list[float] = []

    def proba_um(self, x: list[float]) -> list[float]:
        return softmax([bk + sum(w * v for w, v in zip(wk, x)) for wk, bk in zip(self.W, self.b)])

    def treinar(self, X: list[list[float]], y: list[int]) -> "RegressaoSoftmax":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        n, d, K = len(X), len(X[0]), self.n_classes
        self.W = [[0.0] * d for _ in range(K)]
        self.b = [0.0] * K
        self.perdas = []
        for _ in range(self.iteracoes):
            gW = [[0.0] * d for _ in range(K)]
            gb = [0.0] * K
            perda = 0.0
            for x, r in zip(X, y):
                p = self.proba_um(x)
                perda += entropia_cruzada(r, p)
                for k in range(K):
                    e = p[k] - (1.0 if k == r else 0.0)
                    gb[k] += e
                    for j in range(d):
                        gW[k][j] += e * x[j]
            for k in range(K):
                self.b[k] -= self.taxa * gb[k] / n
                for j in range(d):
                    self.W[k][j] -= self.taxa * gW[k][j] / n
            self.perdas.append(perda / n)
        return self

    def prever(self, X: list[list[float]]) -> list[int]:
        out = []
        for x in X:
            p = self.proba_um(x)
            out.append(p.index(max(p)))
        return out
