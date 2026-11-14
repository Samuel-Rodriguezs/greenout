"""Normalização de dados: min-max, z-score, e suas inversas."""
from __future__ import annotations

import math
from typing import Sequence


def parametros_minmax(dados: Sequence[float]) -> tuple[float, float]:
    if not dados:
        raise ValueError("dados vazios")
    return min(dados), max(dados)


def min_max(dados: Sequence[float], novo_min: float = 0.0, novo_max: float = 1.0) -> list[float]:
    lo, hi = parametros_minmax(dados)
    if hi == lo:
        return [novo_min for _ in dados]
    esc = novo_max - novo_min
    return [novo_min + (x - lo) / (hi - lo) * esc for x in dados]


def desfazer_min_max(
    valores: Sequence[float], lo: float, hi: float, novo_min: float = 0.0, novo_max: float = 1.0
) -> list[float]:
    return [lo + (v - novo_min) / (novo_max - novo_min) * (hi - lo) for v in valores]


def parametros_zscore(dados: Sequence[float]) -> tuple[float, float]:
    if not dados:
        raise ValueError("dados vazios")
    m = sum(dados) / len(dados)
    dp = math.sqrt(sum((x - m) ** 2 for x in dados) / len(dados))
    return m, dp


def z_score(dados: Sequence[float]) -> list[float]:
    m, dp = parametros_zscore(dados)
    if dp == 0:
        return [0.0 for _ in dados]
    return [(x - m) / dp for x in dados]


def desfazer_z_score(valores: Sequence[float], media: float, desvio: float) -> list[float]:
    return [v * desvio + media for v in valores]


def escala_robusta(dados: Sequence[float]) -> list[float]:
    """(x - mediana) / IQR, resistente a outliers."""
    s = sorted(dados)
    if not s:
        raise ValueError("dados vazios")

    def q(p: float) -> float:
        pos = p * (len(s) - 1)
        i = int(pos)
        return s[i] if i + 1 >= len(s) else s[i] + (pos - i) * (s[i + 1] - s[i])

    med, iqr = q(0.5), q(0.75) - q(0.25)
    if iqr == 0:
        return [0.0 for _ in dados]
    return [(x - med) / iqr for x in dados]
