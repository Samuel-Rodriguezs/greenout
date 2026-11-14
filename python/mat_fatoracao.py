"""Fatoração em primos por divisão tentativa e totiente de Euler."""
from collections import Counter
from math import isqrt
from typing import Dict, List


def fatorar(n: int) -> List[int]:
    """Fatores primos com multiplicidade, em ordem crescente."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    fatores: List[int] = []
    while n % 2 == 0:
        fatores.append(2)
        n //= 2
    p = 3
    while p * p <= n:
        while n % p == 0:
            fatores.append(p)
            n //= p
        p += 2
    if n > 1:
        fatores.append(n)
    return fatores


def fatorar_expoentes(n: int) -> Dict[int, int]:
    return dict(sorted(Counter(fatorar(n)).items()))


def divisores(n: int) -> List[int]:
    if n < 1:
        raise ValueError("n deve ser >= 1")
    pequenos, grandes = [], []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            pequenos.append(d)
            if d != n // d:
                grandes.append(n // d)
    return pequenos + grandes[::-1]


def totiente(n: int) -> int:
    r = n
    for p in fatorar_expoentes(n):
        r -= r // p
    return r
