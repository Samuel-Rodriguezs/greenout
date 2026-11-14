"""Integração numérica: regra do trapézio e regra de Simpson."""
from typing import Callable


def trapezio(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    """Integral de f em [a, b] com n subintervalos."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    h = (b - a) / n
    soma = (f(a) + f(b)) / 2
    for i in range(1, n):
        soma += f(a + i * h)
    return soma * h


def simpson(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    """Integral de f em [a, b] por Simpson 1/3; n deve ser par."""
    if n < 2 or n % 2:
        raise ValueError("n deve ser par e >= 2")
    h = (b - a) / n
    soma = f(a) + f(b)
    for i in range(1, n):
        soma += (4 if i % 2 else 2) * f(a + i * h)
    return soma * h / 3
