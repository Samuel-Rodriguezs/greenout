"""Soma de dígitos e raiz digital."""


def soma_digitos(n: int) -> int:
    """Soma os dígitos decimais de n (sinal ignorado)."""
    n = abs(n)
    total = 0
    while n:
        total += n % 10
        n //= 10
    return total


def raiz_digital(n: int) -> int:
    """Repete a soma dos dígitos até restar um único dígito."""
    n = abs(n)
    while n >= 10:
        n = soma_digitos(n)
    return n
