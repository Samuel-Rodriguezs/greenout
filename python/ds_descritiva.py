"""Estatística descritiva: média, mediana, quartis, IQR, assimetria e curtose."""
from __future__ import annotations

import math
from typing import Sequence


def _checar(dados: Sequence[float]) -> list[float]:
    if len(dados) == 0:
        raise ValueError("dados vazios")
    return sorted(dados)


def media(dados: Sequence[float]) -> float:
    _checar(dados)
    return sum(dados) / len(dados)


def mediana(dados: Sequence[float]) -> float:
    s = _checar(dados)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def variancia(dados: Sequence[float], amostral: bool = False) -> float:
    m = media(dados)
    gl = len(dados) - (1 if amostral else 0)
    if gl <= 0:
        raise ValueError("graus de liberdade insuficientes")
    return sum((x - m) ** 2 for x in dados) / gl


def desvio_padrao(dados: Sequence[float], amostral: bool = False) -> float:
    return math.sqrt(variancia(dados, amostral))


def quartis(dados: Sequence[float]) -> tuple[float, float, float]:
    """Q1, Q2, Q3 com interpolação linear (método 7)."""
    s = _checar(dados)

    def q(p: float) -> float:
        pos = p * (len(s) - 1)
        i = int(math.floor(pos))
        f = pos - i
        return s[i] if i + 1 >= len(s) else s[i] + f * (s[i + 1] - s[i])

    return q(0.25), q(0.5), q(0.75)


def iqr(dados: Sequence[float]) -> float:
    q1, _, q3 = quartis(dados)
    return q3 - q1


def assimetria(dados: Sequence[float]) -> float:
    """Coeficiente g1 de Fisher-Pearson (populacional)."""
    m2 = variancia(dados)
    if m2 == 0:
        raise ValueError("variância nula")
    m = media(dados)
    m3 = sum((x - m) ** 3 for x in dados) / len(dados)
    return m3 / m2 ** 1.5


def curtose(dados: Sequence[float]) -> float:
    """Curtose em excesso (normal = 0)."""
    m2 = variancia(dados)
    if m2 == 0:
        raise ValueError("variância nula")
    m = media(dados)
    m4 = sum((x - m) ** 4 for x in dados) / len(dados)
    return m4 / m2 ** 2 - 3


def resumo(dados: Sequence[float]) -> dict[str, float]:
    q1, q2, q3 = quartis(dados)
    return {
        "n": float(len(dados)),
        "min": min(dados),
        "q1": q1,
        "mediana": q2,
        "q3": q3,
        "max": max(dados),
        "media": media(dados),
        "desvio": desvio_padrao(dados, amostral=len(dados) > 1),
        "iqr": q3 - q1,
    }
