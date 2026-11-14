"""Operações com vetores: produto escalar, vetorial, norma e ângulo."""
from math import acos, sqrt
from typing import List, Sequence


def _mesmo_tamanho(a: Sequence[float], b: Sequence[float]) -> None:
    if len(a) != len(b):
        raise ValueError("vetores de tamanhos diferentes")


def soma(a: Sequence[float], b: Sequence[float]) -> List[float]:
    _mesmo_tamanho(a, b)
    return [x + y for x, y in zip(a, b)]


def escalar_por(k: float, a: Sequence[float]) -> List[float]:
    return [k * x for x in a]


def produto_escalar(a: Sequence[float], b: Sequence[float]) -> float:
    _mesmo_tamanho(a, b)
    return sum(x * y for x, y in zip(a, b))


def produto_vetorial(a: Sequence[float], b: Sequence[float]) -> List[float]:
    if len(a) != 3 or len(b) != 3:
        raise ValueError("produto vetorial exige vetores 3D")
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def norma(a: Sequence[float]) -> float:
    return sqrt(produto_escalar(a, a))


def angulo(a: Sequence[float], b: Sequence[float]) -> float:
    """Ângulo em radianos entre dois vetores não nulos."""
    na, nb = norma(a), norma(b)
    if na == 0 or nb == 0:
        raise ValueError("vetor nulo não tem ângulo")
    c = produto_escalar(a, b) / (na * nb)
    return acos(max(-1.0, min(1.0, c)))
