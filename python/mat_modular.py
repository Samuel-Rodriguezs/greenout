"""Aritmética modular: exponenciação rápida, inverso e CRT."""
from typing import Sequence, Tuple


def potencia_modular(base: int, exp: int, mod: int) -> int:
    """base**exp mod mod por quadrados repetidos (exp >= 0)."""
    if mod <= 0:
        raise ValueError("mod deve ser positivo")
    if exp < 0:
        raise ValueError("exp deve ser não negativo")
    r, b = 1 % mod, base % mod
    while exp:
        if exp & 1:
            r = r * b % mod
        b = b * b % mod
        exp >>= 1
    return r


def _egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x, y = _egcd(b, a % b)
    return g, y, x - (a // b) * y


def inverso_modular(a: int, mod: int) -> int:
    if mod <= 0:
        raise ValueError("mod deve ser positivo")
    g, x, _ = _egcd(a % mod, mod)
    if g != 1:
        raise ValueError("inverso não existe")
    return x % mod


def teorema_chines(restos: Sequence[int], modulos: Sequence[int]) -> int:
    """Menor x >= 0 com x ≡ restos[i] (mod modulos[i]); módulos coprimos."""
    if len(restos) != len(modulos) or not restos:
        raise ValueError("listas inválidas")
    x, m = 0, 1
    for r, n in zip(restos, modulos):
        t = ((r - x) * inverso_modular(m, n)) % n
        x += m * t
        m *= n
    return x % m
