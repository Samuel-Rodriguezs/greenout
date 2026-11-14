"""Funções de janela (Hann, Hamming, Blackman) e aplicação a sinais."""
from __future__ import annotations

import math


def _gerar(n: int, coefs: tuple[float, ...]) -> list[float]:
    """Janela cosseno generalizada simétrica: sum (-1)^k a_k cos(2πkm/(n-1))."""
    if n < 0:
        raise ValueError("n não pode ser negativo")
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    return [
        sum((-1) ** k * a * math.cos(2 * math.pi * k * m / (n - 1)) for k, a in enumerate(coefs))
        for m in range(n)
    ]


def retangular(n: int) -> list[float]:
    if n < 0:
        raise ValueError("n não pode ser negativo")
    return [1.0] * n


def hann(n: int) -> list[float]:
    return _gerar(n, (0.5, 0.5))


def hamming(n: int) -> list[float]:
    return _gerar(n, (0.54, 0.46))


def blackman(n: int) -> list[float]:
    return _gerar(n, (0.42, 0.5, 0.08))


def aplicar(x: list[float], janela: list[float]) -> list[float]:
    """Multiplica o sinal pela janela de mesmo tamanho."""
    if len(x) != len(janela):
        raise ValueError("tamanhos diferentes")
    return [a * b for a, b in zip(x, janela)]


def ganho_coerente(janela: list[float]) -> float:
    """Média da janela (ganho coerente)."""
    return sum(janela) / len(janela) if janela else 0.0
