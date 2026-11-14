"""Sequência de Collatz."""
from typing import List


def sequencia(n: int) -> List[int]:
    """Sequência de n até 1."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s


def passos(n: int) -> int:
    return len(sequencia(n)) - 1


def maior_passos_ate(limite: int) -> int:
    """Número <= limite com a maior quantidade de passos (memoizado)."""
    if limite < 1:
        raise ValueError("limite deve ser >= 1")
    cache = {1: 0}

    def custo(n: int) -> int:
        trilha = []
        while n not in cache:
            trilha.append(n)
            n = n // 2 if n % 2 == 0 else 3 * n + 1
        c = cache[n]
        for v in reversed(trilha):
            c += 1
            cache[v] = c
        return c

    return max(range(1, limite + 1), key=lambda i: (custo(i), -i))
