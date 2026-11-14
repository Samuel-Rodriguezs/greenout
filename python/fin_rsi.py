"""Índice de Força Relativa (RSI) com suavização de Wilder."""
from __future__ import annotations


def _rsi_de(ganho: float, perda: float) -> float:
    if ganho == 0 and perda == 0:
        return 50.0
    if perda == 0:
        return 100.0
    return 100 - 100 / (1 + ganho / perda)


def rsi(precos: list[float], n: int = 14) -> list[float | None]:
    """RSI de período n; as n primeiras posições são None."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    saida: list[float | None] = [None] * len(precos)
    if len(precos) <= n:
        return saida
    difs = [precos[i] - precos[i - 1] for i in range(1, len(precos))]
    ganho = sum(max(d, 0.0) for d in difs[:n]) / n
    perda = sum(max(-d, 0.0) for d in difs[:n]) / n
    saida[n] = _rsi_de(ganho, perda)
    for i in range(n, len(difs)):
        d = difs[i]
        ganho = (ganho * (n - 1) + max(d, 0.0)) / n
        perda = (perda * (n - 1) + max(-d, 0.0)) / n
        saida[i + 1] = _rsi_de(ganho, perda)
    return saida
