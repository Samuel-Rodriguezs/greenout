"""Trailing Zeros Kata: zeros finais do fatorial sem calcular o fatorial."""
from __future__ import annotations


def zeros_fatorial(n: int, base: int = 10) -> int:
    """Número de zeros à direita de n! escrito na base dada (fórmula de Legendre)."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    if base < 2:
        raise ValueError("base deve ser >= 2")
    # Fatora a base e toma o gargalo entre os primos.
    expoentes: dict[int, int] = {}
    b, p = base, 2
    while p * p <= b:
        while b % p == 0:
            expoentes[p] = expoentes.get(p, 0) + 1
            b //= p
        p += 1
    if b > 1:
        expoentes[b] = expoentes.get(b, 0) + 1
    menor = None
    for primo, exp in expoentes.items():
        total, potencia = 0, primo
        while potencia <= n:
            total += n // potencia
            potencia *= primo
        candidato = total // exp
        menor = candidato if menor is None else min(menor, candidato)
    return menor or 0
