"""Coeficiente de correlação de Pearson."""
from math import sqrt
from typing import Sequence


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y):
        raise ValueError("x e y devem ter o mesmo tamanho")
    if len(x) < 2:
        raise ValueError("são necessários ao menos 2 pontos")
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        raise ValueError("variância nula: correlação indefinida")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / sqrt(sxx * syy)
