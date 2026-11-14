"""Prime Factors Kata."""
from __future__ import annotations


def fatores_primos(n: int) -> list[int]:
    """Lista os fatores primos de n em ordem crescente (com repetição)."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    fatores: list[int] = []
    divisor = 2
    while n > 1:
        while n % divisor == 0:
            fatores.append(divisor)
            n //= divisor
        divisor += 1 if divisor == 2 else 2
        if divisor * divisor > n and n > 1:
            fatores.append(n)
            break
    return fatores
