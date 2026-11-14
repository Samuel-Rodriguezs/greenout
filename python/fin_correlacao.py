"""Correlação de Pearson entre ativos e matriz de correlação."""
from __future__ import annotations

import math


def correlacao(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("séries com tamanhos diferentes")
    if len(a) < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    saa = sum((x - ma) ** 2 for x in a)
    sbb = sum((y - mb) ** 2 for y in b)
    if saa == 0 or sbb == 0:
        raise ValueError("série sem variância")
    return sab / math.sqrt(saa * sbb)


def matriz_correlacao(series: dict[str, list[float]]) -> dict[str, dict[str, float]]:
    nomes = list(series)
    matriz: dict[str, dict[str, float]] = {n: {} for n in nomes}
    for i, x in enumerate(nomes):
        matriz[x][x] = 1.0
        for y in nomes[i + 1 :]:
            c = correlacao(series[x], series[y])
            matriz[x][y] = matriz[y][x] = c
    return matriz
