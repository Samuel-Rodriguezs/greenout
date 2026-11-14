"""Regressão linear simples por mínimos quadrados."""
from typing import Sequence, Tuple


def regressao_linear(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    """Retorna (a, b) de y = a*x + b."""
    if len(x) != len(y):
        raise ValueError("x e y devem ter o mesmo tamanho")
    if len(x) < 2:
        raise ValueError("são necessários ao menos 2 pontos")
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        raise ValueError("x constante: regressão indefinida")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    a = sxy / sxx
    return a, my - a * mx


def prever(coef: Tuple[float, float], x: float) -> float:
    return coef[0] * x + coef[1]


def r_quadrado(x: Sequence[float], y: Sequence[float]) -> float:
    a, b = regressao_linear(x, y)
    my = sum(y) / len(y)
    sst = sum((v - my) ** 2 for v in y)
    if sst == 0:
        return 1.0
    sse = sum((v - (a * u + b)) ** 2 for u, v in zip(x, y))
    return 1 - sse / sst
