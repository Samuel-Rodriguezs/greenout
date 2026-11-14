"""Mixagem, normalização, ganho em dB e fades."""
from __future__ import annotations

import math


def ganho_db(x: list[float], db: float) -> list[float]:
    """Aplica ganho em decibéis."""
    g = 10 ** (db / 20)
    return [v * g for v in x]


def misturar(sinais: list[list[float]], pesos: list[float] | None = None) -> list[float]:
    """Soma ponderada; sinais mais curtos são completados com zeros."""
    if not sinais:
        return []
    if pesos is None:
        pesos = [1.0] * len(sinais)
    if len(pesos) != len(sinais):
        raise ValueError("pesos e sinais com tamanhos diferentes")
    n = max(len(s) for s in sinais)
    saida = [0.0] * n
    for s, p in zip(sinais, pesos):
        for i, v in enumerate(s):
            saida[i] += p * v
    return saida


def pico(x: list[float]) -> float:
    return max((abs(v) for v in x), default=0.0)


def normalizar(x: list[float], alvo: float = 1.0) -> list[float]:
    """Escala para que o pico absoluto seja `alvo`; silêncio fica inalterado."""
    if alvo < 0:
        raise ValueError("alvo não pode ser negativo")
    p = pico(x)
    if p == 0:
        return list(x)
    return [v * alvo / p for v in x]


def remover_dc(x: list[float]) -> list[float]:
    if not x:
        return []
    m = sum(x) / len(x)
    return [v - m for v in x]


def fade_in(x: list[float], n: int, curva: str = "linear") -> list[float]:
    """Rampa de 0 a 1 nas primeiras n amostras."""
    return _fade(x, n, entrada=True, curva=curva)


def fade_out(x: list[float], n: int, curva: str = "linear") -> list[float]:
    """Rampa de 1 a 0 nas últimas n amostras."""
    return _fade(x, n, entrada=False, curva=curva)


def _fade(x: list[float], n: int, entrada: bool, curva: str) -> list[float]:
    if n < 0:
        raise ValueError("n não pode ser negativo")
    if curva not in ("linear", "cosseno"):
        raise ValueError("curva desconhecida")
    n = min(n, len(x))
    saida = list(x)
    for i in range(n):
        t = i / (n - 1) if n > 1 else 1.0
        if curva == "cosseno":
            t = (1 - math.cos(math.pi * t)) / 2
        if entrada:
            saida[i] = x[i] * t
        else:
            saida[len(x) - n + i] = x[len(x) - n + i] * (1 - t)
    return saida


def crossfade(a: list[float], b: list[float], n: int) -> list[float]:
    """Concatena a e b sobrepondo n amostras com fade linear."""
    n = min(n, len(a), len(b))
    if n < 0:
        raise ValueError("n não pode ser negativo")
    meio = [
        a[len(a) - n + i] * (1 - (i + 1) / (n + 1)) + b[i] * ((i + 1) / (n + 1))
        for i in range(n)
    ]
    return a[: len(a) - n] + meio + b[n:]
