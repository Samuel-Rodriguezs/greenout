"""Percentis por interpolação linear, posto mais próximo e posto percentil."""
from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from typing import Sequence


def _ordenar(dados: Sequence[float]) -> list[float]:
    if not dados:
        raise ValueError("dados vazios")
    return sorted(dados)


def _checar_p(p: float) -> None:
    if not 0 <= p <= 100:
        raise ValueError("percentil deve estar em [0, 100]")


def percentil(dados: Sequence[float], p: float) -> float:
    """Interpolação linear entre os postos (método 7 do R/NumPy)."""
    _checar_p(p)
    s = _ordenar(dados)
    pos = p / 100 * (len(s) - 1)
    i = int(math.floor(pos))
    if i + 1 >= len(s):
        return s[-1]
    return s[i] + (pos - i) * (s[i + 1] - s[i])


def percentil_posto_proximo(dados: Sequence[float], p: float) -> float:
    """Método do posto mais próximo: menor valor com ao menos p% dos dados <= ele."""
    _checar_p(p)
    s = _ordenar(dados)
    if p == 0:
        return s[0]
    return s[math.ceil(p / 100 * len(s)) - 1]


def percentis(dados: Sequence[float], ps: Sequence[float]) -> dict[float, float]:
    return {p: percentil(dados, p) for p in ps}


def posto_percentil(dados: Sequence[float], valor: float) -> float:
    """Percentual de dados abaixo do valor, contando metade dos empates."""
    s = _ordenar(dados)
    abaixo = bisect_left(s, valor)
    igual = bisect_right(s, valor) - abaixo
    return (abaixo + 0.5 * igual) / len(s) * 100
