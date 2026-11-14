"""Combinatória: fatorial, combinações, arranjos e permutações."""
from itertools import permutations
from typing import Iterator, Sequence, Tuple, TypeVar

T = TypeVar("T")


def fatorial(n: int) -> int:
    if n < 0:
        raise ValueError("n deve ser não negativo")
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def combinacao(n: int, k: int) -> int:
    """C(n, k) sem calcular fatoriais completos."""
    if n < 0 or k < 0:
        raise ValueError("n e k devem ser não negativos")
    if k > n:
        return 0
    k = min(k, n - k)
    r = 1
    for i in range(1, k + 1):
        r = r * (n - k + i) // i
    return r


def arranjo(n: int, k: int) -> int:
    """A(n, k) = n! / (n-k)!"""
    if n < 0 or k < 0:
        raise ValueError("n e k devem ser não negativos")
    if k > n:
        return 0
    r = 1
    for i in range(n - k + 1, n + 1):
        r *= i
    return r


def permutacoes(itens: Sequence[T]) -> Iterator[Tuple[T, ...]]:
    return permutations(itens)


def permutacoes_com_repeticao(itens: Sequence[T]) -> int:
    """Número de anagramas distintos de uma sequência com repetições."""
    r = fatorial(len(itens))
    for v in set(itens):
        r //= fatorial(list(itens).count(v))
    return r
