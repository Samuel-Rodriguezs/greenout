"""Regularização L1 (lasso, coordenada descendente) e L2 (ridge, solução fechada)."""
from __future__ import annotations


def _resolver(A: list[list[float]], b: list[float]) -> list[float]:
    """Eliminação gaussiana com pivotamento parcial."""
    n = len(A)
    M = [linha[:] + [b[i]] for i, linha in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise ValueError("matriz singular")
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def _centralizar(X, y):
    n = len(X)
    mx = [sum(c) / n for c in zip(*X)]
    my = sum(y) / n
    return [[v - m for v, m in zip(x, mx)] for x in X], [v - my for v in y], mx, my


def penalidade_l1(pesos: list[float], alfa: float) -> float:
    return alfa * sum(abs(w) for w in pesos)


def penalidade_l2(pesos: list[float], alfa: float) -> float:
    return alfa * sum(w * w for w in pesos)


def ridge(X: list[list[float]], y: list[float], alfa: float) -> tuple[list[float], float]:
    """Mínimos quadrados com penalidade L2 (intercepto não penalizado). Retorna (pesos, intercepto)."""
    if alfa < 0:
        raise ValueError("alfa deve ser >= 0")
    Xc, yc, mx, my = _centralizar(X, y)
    d = len(Xc[0])
    A = [[sum(x[i] * x[j] for x in Xc) + (alfa if i == j else 0.0) for j in range(d)] for i in range(d)]
    b = [sum(x[i] * v for x, v in zip(Xc, yc)) for i in range(d)]
    w = _resolver(A, b)
    return w, my - sum(a * c for a, c in zip(w, mx))


def _suave(z: float, lim: float) -> float:
    if z > lim:
        return z - lim
    if z < -lim:
        return z + lim
    return 0.0


def lasso(X: list[list[float]], y: list[float], alfa: float, iteracoes: int = 200,
          tol: float = 1e-9) -> tuple[list[float], float]:
    """Lasso por coordenada descendente com soft-thresholding. Retorna (pesos, intercepto)."""
    if alfa < 0:
        raise ValueError("alfa deve ser >= 0")
    Xc, yc, mx, my = _centralizar(X, y)
    n, d = len(Xc), len(Xc[0])
    w = [0.0] * d
    norma = [sum(x[j] ** 2 for x in Xc) for j in range(d)]
    for _ in range(iteracoes):
        maior = 0.0
        for j in range(d):
            if norma[j] == 0:
                continue
            rho = sum(Xc[i][j] * (yc[i] - sum(Xc[i][k] * w[k] for k in range(d)) + Xc[i][j] * w[j])
                      for i in range(n))
            novo = _suave(rho, alfa * n) / norma[j]
            maior = max(maior, abs(novo - w[j]))
            w[j] = novo
        if maior < tol:
            break
    return w, my - sum(a * c for a, c in zip(w, mx))
