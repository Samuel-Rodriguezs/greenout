"""Médias móveis simples (SMA) e exponencial (EMA) de uma série de preços."""
from __future__ import annotations


def sma(precos: list[float], n: int) -> list[float | None]:
    """SMA de janela n; as n-1 primeiras posições são None."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    saida: list[float | None] = [None] * len(precos)
    soma = 0.0
    for i, p in enumerate(precos):
        soma += p
        if i >= n:
            soma -= precos[i - n]
        if i >= n - 1:
            saida[i] = soma / n
    return saida


def ema(precos: list[float], n: int) -> list[float | None]:
    """EMA com alpha = 2/(n+1), semeada pela SMA dos n primeiros preços."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    saida: list[float | None] = [None] * len(precos)
    if len(precos) < n:
        return saida
    alfa = 2 / (n + 1)
    atual = sum(precos[:n]) / n
    saida[n - 1] = atual
    for i in range(n, len(precos)):
        atual = alfa * precos[i] + (1 - alfa) * atual
        saida[i] = atual
    return saida
