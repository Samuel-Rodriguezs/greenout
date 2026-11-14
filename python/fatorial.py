"""Fatorial nas versões iterativa e recursiva."""


def fatorial_iterativo(n: int) -> int:
    """Calcula n! com laço; levanta ValueError para n negativo."""
    if n < 0:
        raise ValueError("fatorial não definido para números negativos")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


def fatorial_recursivo(n: int) -> int:
    """Calcula n! recursivamente; levanta ValueError para n negativo."""
    if n < 0:
        raise ValueError("fatorial não definido para números negativos")
    if n <= 1:
        return 1
    return n * fatorial_recursivo(n - 1)
