"""PCA por iteração de potência com deflação."""
from __future__ import annotations

import math


def centralizar(X: list[list[float]]) -> tuple[list[list[float]], list[float]]:
    medias = [sum(c) / len(X) for c in zip(*X)]
    return [[v - m for v, m in zip(x, medias)] for x in X], medias


def covariancia(Xc: list[list[float]]) -> list[list[float]]:
    n, d = len(Xc), len(Xc[0])
    return [[sum(x[i] * x[j] for x in Xc) / (n - 1) for j in range(d)] for i in range(d)]


def _matvec(M: list[list[float]], v: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(linha, v)) for linha in M]


def potencia(M: list[list[float]], iteracoes: int = 500, tol: float = 1e-12) -> tuple[float, list[float]]:
    """Autovalor dominante e autovetor unitário."""
    d = len(M)
    v = [1.0 / math.sqrt(d) + 0.01 * i for i in range(d)]
    norma = math.sqrt(sum(a * a for a in v))
    v = [a / norma for a in v]
    lam = 0.0
    for _ in range(iteracoes):
        w = _matvec(M, v)
        norma = math.sqrt(sum(a * a for a in w))
        if norma == 0:
            return 0.0, v
        w = [a / norma for a in w]
        novo = sum(a * b for a, b in zip(w, _matvec(M, w)))
        if abs(novo - lam) < tol and all(abs(a - b) < 1e-10 for a, b in zip(w, v)):
            v, lam = w, novo
            break
        v, lam = w, novo
    # sinal canônico: maior componente em módulo positiva
    i = max(range(d), key=lambda k: abs(v[k]))
    if v[i] < 0:
        v = [-a for a in v]
    return lam, v


class PCA:
    def __init__(self, n_componentes: int = 2) -> None:
        self.n_componentes = n_componentes
        self.medias: list[float] = []
        self.componentes: list[list[float]] = []
        self.variancias: list[float] = []
        self.variancia_total = 0.0

    def ajustar(self, X: list[list[float]]) -> "PCA":
        if len(X) < 2:
            raise ValueError("são necessárias ao menos 2 amostras")
        d = len(X[0])
        if not 1 <= self.n_componentes <= d:
            raise ValueError("n_componentes fora do intervalo")
        Xc, self.medias = centralizar(X)
        C = covariancia(Xc)
        self.variancia_total = sum(C[i][i] for i in range(d))
        self.componentes, self.variancias = [], []
        for _ in range(self.n_componentes):
            lam, v = potencia(C)
            self.componentes.append(v)
            self.variancias.append(lam)
            C = [[C[i][j] - lam * v[i] * v[j] for j in range(d)] for i in range(d)]
        return self

    def transformar(self, X: list[list[float]]) -> list[list[float]]:
        return [[sum((a - m) * c for a, m, c in zip(x, self.medias, comp)) for comp in self.componentes]
                for x in X]

    def razao_variancia(self) -> list[float]:
        return [v / self.variancia_total for v in self.variancias]
