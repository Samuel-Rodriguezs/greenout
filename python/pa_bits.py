"""Truques com operadores bit a bit."""
from typing import List, Tuple


def eh_potencia_de_dois(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def contar_bits(n: int) -> int:
    """Algoritmo de Kernighan para inteiros não negativos."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c


def bit_menos_significativo(n: int) -> int:
    """Isola o bit 1 mais baixo (0 se n == 0)."""
    return n & -n


def trocar_sem_temporaria(a: int, b: int) -> Tuple[int, int]:
    a ^= b
    b ^= a
    a ^= b
    return a, b


def inverter_bits(n: int, largura: int = 8) -> int:
    """Espelha a ordem dos bits de n dentro da largura dada."""
    if largura < 1 or not 0 <= n < (1 << largura):
        raise ValueError("n não cabe na largura")
    r = 0
    for _ in range(largura):
        r = (r << 1) | (n & 1)
        n >>= 1
    return r


def unico_elemento(numeros: List[int]) -> int:
    """Em uma lista onde todos se repetem duas vezes, devolve o que aparece uma vez."""
    r = 0
    for x in numeros:
        r ^= x
    return r


def subconjuntos(itens: list) -> List[list]:
    """Todos os subconjuntos via máscara de bits."""
    n = len(itens)
    return [[itens[i] for i in range(n) if m >> i & 1] for m in range(1 << n)]
