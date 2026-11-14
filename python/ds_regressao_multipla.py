"""Regressão linear múltipla por mínimos quadrados (equações normais)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class ModeloLinear:
    intercepto: float
    coeficientes: list[float]
    r2: float

    def prever(self, x: Sequence[float]) -> float:
        if len(x) != len(self.coeficientes):
            raise ValueError("número de variáveis incompatível")
        return self.intercepto + sum(c * v for c, v in zip(self.coeficientes, x))


def _resolver(a: list[list[float]], b: list[float]) -> list[float]:
    """Eliminação de Gauss com pivotamento parcial."""
    n = len(b)
    m = [linha[:] + [b[i]] for i, linha in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            raise ValueError("variáveis colineares: sistema singular")
        m[col], m[piv] = m[piv], m[col]
        for r in range(col + 1, n):
            f = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= f * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))) / m[i][i]
    return x


def ajustar(X: Sequence[Sequence[float]], y: Sequence[float]) -> ModeloLinear:
    """X: linhas de observações (sem coluna de 1s)."""
    n = len(X)
    if n != len(y) or n == 0:
        raise ValueError("X e y devem ter o mesmo tamanho (não vazio)")
    p = len(X[0])
    if any(len(l) != p for l in X):
        raise ValueError("linhas de X com tamanhos diferentes")
    if n < p + 1:
        raise ValueError("observações insuficientes")
    A = [[1.0, *map(float, l)] for l in X]
    k = p + 1
    xtx = [[sum(A[r][i] * A[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    xty = [sum(A[r][i] * y[r] for r in range(n)) for i in range(k)]
    beta = _resolver(xtx, xty)
    media_y = sum(y) / n
    sst = sum((v - media_y) ** 2 for v in y)
    sse = sum((y[r] - sum(beta[i] * A[r][i] for i in range(k))) ** 2 for r in range(n))
    r2 = 1.0 if sst == 0 else 1 - sse / sst
    return ModeloLinear(beta[0], beta[1:], r2)
