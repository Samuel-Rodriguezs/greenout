"""Correlação de postos de Spearman (com empates por posto médio)."""
from __future__ import annotations

import math
from typing import Sequence


def postos(dados: Sequence[float]) -> list[float]:
    """Postos 1..n; empates recebem a média dos postos ocupados."""
    ordem = sorted(range(len(dados)), key=lambda i: dados[i])
    r = [0.0] * len(dados)
    i = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and dados[ordem[j + 1]] == dados[ordem[i]]:
            j += 1
        medio = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[ordem[k]] = medio
        i = j + 1
    return r


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        raise ValueError("variância nula: correlação indefinida")
    return sxy / math.sqrt(sxx * syy)


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y):
        raise ValueError("séries de tamanhos diferentes")
    if len(x) < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    return _pearson(postos(x), postos(y))


def spearman_p_valor(rho: float, n: int) -> float:
    """p-valor bilateral aproximado (t com n-2 gl, via normal para n grande)."""
    if n < 3:
        raise ValueError("n deve ser >= 3")
    if abs(rho) >= 1:
        return 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    # aproximação normal corrigida (Cornish-Fisher simples) da cauda t
    gl = n - 2
    z = t * (1 - 1 / (4 * gl)) / math.sqrt(1 + t * t / (2 * gl))
    return math.erfc(abs(z) / math.sqrt(2))
