"""DFT direta e FFT radix-2 (iterativa) com inversa."""
from __future__ import annotations

import cmath


def dft(x: list[complex]) -> list[complex]:
    """DFT direta O(n^2)."""
    n = len(x)
    return [
        sum(x[t] * cmath.exp(-2j * cmath.pi * k * t / n) for t in range(n))
        for k in range(n)
    ]


def idft(X: list[complex]) -> list[complex]:
    """Inversa da DFT direta."""
    n = len(X)
    return [
        sum(X[k] * cmath.exp(2j * cmath.pi * k * t / n) for k in range(n)) / n
        for t in range(n)
    ]


def potencia_de_dois(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def proxima_potencia_de_dois(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def _fft(x: list[complex], sinal: int) -> list[complex]:
    n = len(x)
    if not potencia_de_dois(n):
        raise ValueError("tamanho deve ser potência de 2")
    a = [complex(v) for v in x]
    # permutação por bit-reversal
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    tam = 2
    while tam <= n:
        w_tam = cmath.exp(sinal * 2j * cmath.pi / tam)
        for ini in range(0, n, tam):
            w = 1 + 0j
            for k in range(tam // 2):
                u = a[ini + k]
                v = a[ini + k + tam // 2] * w
                a[ini + k] = u + v
                a[ini + k + tam // 2] = u - v
                w *= w_tam
        tam <<= 1
    return a


def fft(x: list[complex]) -> list[complex]:
    """FFT radix-2; len(x) deve ser potência de 2."""
    return _fft(x, -1)


def ifft(X: list[complex]) -> list[complex]:
    """Inversa da FFT (normalizada por 1/n)."""
    n = len(X)
    return [v / n for v in _fft(X, +1)]


def fft_zero_pad(x: list[float]) -> list[complex]:
    """FFT após completar com zeros até a próxima potência de 2."""
    n = proxima_potencia_de_dois(max(len(x), 1))
    return fft(list(x) + [0.0] * (n - len(x)))
