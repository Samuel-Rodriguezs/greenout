"""Crivo de Eratóstenes segmentado."""
from math import isqrt
from typing import List


def crivo_simples(limite: int) -> List[int]:
    """Primos <= limite."""
    if limite < 2:
        return []
    marcas = bytearray([1]) * (limite + 1)
    marcas[0] = marcas[1] = 0
    for i in range(2, isqrt(limite) + 1):
        if marcas[i]:
            marcas[i * i::i] = bytearray(len(range(i * i, limite + 1, i)))
    return [i for i, m in enumerate(marcas) if m]


def primos_no_intervalo(a: int, b: int) -> List[int]:
    """Primos em [a, b] usando apenas primos até sqrt(b)."""
    if b < 2 or a > b:
        return []
    a = max(a, 2)
    base = crivo_simples(isqrt(b))
    marcas = bytearray([1]) * (b - a + 1)
    for p in base:
        inicio = max(p * p, ((a + p - 1) // p) * p)
        if inicio > b:
            continue
        marcas[inicio - a::p] = bytearray(len(range(inicio, b + 1, p)))
    return [a + i for i, m in enumerate(marcas) if m]
