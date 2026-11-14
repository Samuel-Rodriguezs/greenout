"""Convolução e correlação discretas."""
from __future__ import annotations


def convolucao(x: list[float], h: list[float]) -> list[float]:
    """Convolução linear completa (tamanho len(x)+len(h)-1)."""
    if not x or not h:
        return []
    y = [0.0] * (len(x) + len(h) - 1)
    for i, a in enumerate(x):
        for j, b in enumerate(h):
            y[i + j] += a * b
    return y


def convolucao_mesma(x: list[float], h: list[float]) -> list[float]:
    """Parte central da convolução, com o tamanho de x."""
    y = convolucao(x, h)
    if not y:
        return []
    ini = (len(h) - 1) // 2
    return y[ini:ini + len(x)]


def correlacao_cruzada(x: list[float], y: list[float]) -> list[float]:
    """r[k] = sum x[n+k] y[n], com lags de -(len(y)-1) a len(x)-1."""
    if not x or not y:
        return []
    return convolucao(x, y[::-1])


def autocorrelacao(x: list[float]) -> list[float]:
    """Autocorrelação para lags 0..len(x)-1."""
    n = len(x)
    return [sum(x[i] * x[i + k] for i in range(n - k)) for k in range(n)]


def lag_do_maximo(x: list[float], y: list[float]) -> int:
    """Atraso k que maximiza a correlação (x[n+k] ~ y[n])."""
    r = correlacao_cruzada(x, y)
    if not r:
        raise ValueError("sinais vazios")
    melhor = max(range(len(r)), key=lambda i: r[i])
    return melhor - (len(y) - 1)
