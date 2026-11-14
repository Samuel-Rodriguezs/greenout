"""Espectro de magnitude e fase de sinais reais via FFT."""
from __future__ import annotations

import cmath
import math

from sig_fft import fft_zero_pad


def espectro(x: list[float]) -> list[complex]:
    """Metade não redundante do espectro (0..N/2) com zero-padding."""
    X = fft_zero_pad(x)
    return X[: len(X) // 2 + 1]


def magnitude(x: list[float]) -> list[float]:
    """Magnitude normalizada: um seno de amplitude A em bin exato dá A."""
    X = fft_zero_pad(x)
    n = len(X)
    metade = X[: n // 2 + 1]
    mags = [2 * abs(v) / n for v in metade]
    mags[0] /= 2
    if n % 2 == 0 and n > 1:
        mags[-1] /= 2
    return mags


def fase(x: list[float], limiar: float = 1e-9) -> list[float]:
    """Fase em radianos; bins com magnitude abaixo do limiar têm fase 0."""
    return [cmath.phase(v) if abs(v) > limiar else 0.0 for v in espectro(x)]


def frequencias(n: int, taxa: float) -> list[float]:
    """Frequências (Hz) dos bins 0..n/2 de uma FFT de tamanho n."""
    if n <= 0 or taxa <= 0:
        raise ValueError("n e taxa devem ser positivos")
    return [k * taxa / n for k in range(n // 2 + 1)]


def frequencia_dominante(x: list[float], taxa: float) -> float:
    """Frequência do bin de maior magnitude, ignorando DC."""
    if len(x) < 2:
        raise ValueError("sinal curto demais")
    mags = magnitude(x)
    n = (len(mags) - 1) * 2
    k = max(range(1, len(mags)), key=lambda i: mags[i])
    return k * taxa / n


def magnitude_db(x: list[float], piso: float = 1e-12) -> list[float]:
    """Magnitude em dB (20 log10), com piso para evitar log(0)."""
    return [20 * math.log10(max(m, piso)) for m in magnitude(x)]
