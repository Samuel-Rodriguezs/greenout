"""Derivação numérica por diferenças finitas."""
from typing import Callable


def diferenca_progressiva(f: Callable[[float], float], x: float, h: float = 1e-6) -> float:
    return (f(x + h) - f(x)) / h


def diferenca_regressiva(f: Callable[[float], float], x: float, h: float = 1e-6) -> float:
    return (f(x) - f(x - h)) / h


def diferenca_central(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """Derivada de ordem 1 com erro O(h^2)."""
    return (f(x + h) - f(x - h)) / (2 * h)


def segunda_derivada(f: Callable[[float], float], x: float, h: float = 1e-3) -> float:
    return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)
