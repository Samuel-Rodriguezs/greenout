"""Geradores de formas de onda discretas."""
from __future__ import annotations

import math
import random


def _validar(freq: float, taxa: float, n: int) -> None:
    if taxa <= 0:
        raise ValueError("taxa de amostragem deve ser positiva")
    if n < 0:
        raise ValueError("n não pode ser negativo")
    if freq < 0:
        raise ValueError("frequência não pode ser negativa")


def _fase(i: int, freq: float, taxa: float) -> float:
    """Fase normalizada em [0, 1) da amostra i."""
    return (freq * i / taxa) % 1.0


def senoidal(freq: float, taxa: float, n: int, amp: float = 1.0, fase: float = 0.0) -> list[float]:
    """Seno; `fase` em ciclos (0..1)."""
    _validar(freq, taxa, n)
    return [amp * math.sin(2 * math.pi * (freq * i / taxa + fase)) for i in range(n)]


def quadrada(freq: float, taxa: float, n: int, amp: float = 1.0, ciclo: float = 0.5) -> list[float]:
    """Onda quadrada com ciclo de trabalho `ciclo` (0..1)."""
    _validar(freq, taxa, n)
    if not 0 < ciclo < 1:
        raise ValueError("ciclo deve estar em (0, 1)")
    return [amp if _fase(i, freq, taxa) < ciclo else -amp for i in range(n)]


def dente_de_serra(freq: float, taxa: float, n: int, amp: float = 1.0) -> list[float]:
    """Rampa de -amp a +amp a cada período."""
    _validar(freq, taxa, n)
    return [amp * (2 * _fase(i, freq, taxa) - 1) for i in range(n)]


def triangular(freq: float, taxa: float, n: int, amp: float = 1.0) -> list[float]:
    """Triangular começando em -amp, com pico em meio período."""
    _validar(freq, taxa, n)
    return [amp * (1 - 4 * abs(_fase(i, freq, taxa) - 0.5)) for i in range(n)]


def ruido_branco(n: int, amp: float = 1.0, seed: int = 0) -> list[float]:
    """Ruído uniforme em [-amp, amp], reprodutível por seed."""
    if n < 0:
        raise ValueError("n não pode ser negativo")
    rng = random.Random(seed)
    return [amp * (2 * rng.random() - 1) for _ in range(n)]


def rms(x: list[float]) -> float:
    """Valor eficaz do sinal."""
    if not x:
        return 0.0
    return math.sqrt(sum(v * v for v in x) / len(x))
