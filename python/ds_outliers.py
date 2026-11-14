"""Detecção de outliers por IQR (Tukey) e por z-score."""
from __future__ import annotations

import math
from typing import Sequence


def _quartis(dados: Sequence[float]) -> tuple[float, float]:
    s = sorted(dados)

    def q(p: float) -> float:
        pos = p * (len(s) - 1)
        i = int(pos)
        return s[i] if i + 1 >= len(s) else s[i] + (pos - i) * (s[i + 1] - s[i])

    return q(0.25), q(0.75)


def limites_iqr(dados: Sequence[float], k: float = 1.5) -> tuple[float, float]:
    if not dados:
        raise ValueError("dados vazios")
    q1, q3 = _quartis(dados)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def outliers_iqr(dados: Sequence[float], k: float = 1.5) -> list[int]:
    """Índices dos valores fora de [Q1 - k*IQR, Q3 + k*IQR]."""
    inf, sup = limites_iqr(dados, k)
    return [i for i, x in enumerate(dados) if x < inf or x > sup]


def zscores(dados: Sequence[float]) -> list[float]:
    if not dados:
        raise ValueError("dados vazios")
    m = sum(dados) / len(dados)
    dp = math.sqrt(sum((x - m) ** 2 for x in dados) / len(dados))
    if dp == 0:
        return [0.0] * len(dados)
    return [(x - m) / dp for x in dados]


def outliers_zscore(dados: Sequence[float], limite: float = 3.0) -> list[int]:
    """Índices com |z| maior que o limite."""
    return [i for i, z in enumerate(zscores(dados)) if abs(z) > limite]


def remover_outliers(dados: Sequence[float], metodo: str = "iqr", **kw: float) -> list[float]:
    if metodo == "iqr":
        idx = set(outliers_iqr(dados, **kw))
    elif metodo == "zscore":
        idx = set(outliers_zscore(dados, **kw))
    else:
        raise ValueError("método deve ser 'iqr' ou 'zscore'")
    return [x for i, x in enumerate(dados) if i not in idx]
