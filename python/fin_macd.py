"""MACD: diferença entre EMAs rápida e lenta, linha de sinal e histograma."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoMACD:
    macd: list[float]
    sinal: list[float]
    histograma: list[float]


def ema_continua(valores: list[float], n: int) -> list[float]:
    """EMA com alpha = 2/(n+1) semeada pelo primeiro valor (sem None)."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    alfa = 2 / (n + 1)
    saida: list[float] = []
    for v in valores:
        saida.append(v if not saida else alfa * v + (1 - alfa) * saida[-1])
    return saida


def macd(
    precos: list[float], rapida: int = 12, lenta: int = 26, sinal: int = 9
) -> ResultadoMACD:
    if rapida >= lenta:
        raise ValueError("a média rápida deve ter período menor que a lenta")
    er = ema_continua(precos, rapida)
    el = ema_continua(precos, lenta)
    linha = [a - b for a, b in zip(er, el)]
    sig = ema_continua(linha, sinal)
    return ResultadoMACD(linha, sig, [m - s for m, s in zip(linha, sig)])
