"""Máximo divisor comum (MDC) e mínimo múltiplo comum (MMC)."""


def mdc(a: int, b: int) -> int:
    """Calcula o MDC pelo algoritmo de Euclides; sempre retorna valor não negativo."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def mmc(a: int, b: int) -> int:
    """Calcula o MMC; retorna 0 se algum dos números for 0."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // mdc(a, b)
