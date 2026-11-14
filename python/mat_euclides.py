"""Algoritmo de Euclides: MDC, MMC e Euclides estendido."""
from typing import Tuple


def mdc(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def mmc(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return abs(a // mdc(a, b) * b)


def euclides_estendido(a: int, b: int) -> Tuple[int, int, int]:
    """Retorna (g, x, y) com a*x + b*y = g = mdc(a, b)."""
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    if a < 0:
        return -a, -x0, -y0
    return a, x0, y0
