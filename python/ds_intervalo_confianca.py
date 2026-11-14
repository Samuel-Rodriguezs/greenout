"""Intervalos de confiança: média (z e t) e proporção (Wald e Wilson)."""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Sequence

from ds_teste_t import t_ppf


def _media_erro(dados: Sequence[float]) -> tuple[float, float]:
    n = len(dados)
    if n < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    m = sum(dados) / n
    s = math.sqrt(sum((x - m) ** 2 for x in dados) / (n - 1))
    return m, s / math.sqrt(n)


def _checar_conf(confianca: float) -> None:
    if not 0 < confianca < 1:
        raise ValueError("confiança deve estar em (0, 1)")


def ic_media_z(dados: Sequence[float], confianca: float = 0.95) -> tuple[float, float]:
    _checar_conf(confianca)
    m, ep = _media_erro(dados)
    z = NormalDist().inv_cdf((1 + confianca) / 2)
    return m - z * ep, m + z * ep


def ic_media_t(dados: Sequence[float], confianca: float = 0.95) -> tuple[float, float]:
    _checar_conf(confianca)
    m, ep = _media_erro(dados)
    t = t_ppf((1 + confianca) / 2, len(dados) - 1)
    return m - t * ep, m + t * ep


def ic_proporcao_wald(sucessos: int, n: int, confianca: float = 0.95) -> tuple[float, float]:
    _checar_conf(confianca)
    if n <= 0 or not 0 <= sucessos <= n:
        raise ValueError("contagens inválidas")
    p = sucessos / n
    z = NormalDist().inv_cdf((1 + confianca) / 2)
    h = z * math.sqrt(p * (1 - p) / n)
    return max(0.0, p - h), min(1.0, p + h)


def ic_proporcao_wilson(sucessos: int, n: int, confianca: float = 0.95) -> tuple[float, float]:
    _checar_conf(confianca)
    if n <= 0 or not 0 <= sucessos <= n:
        raise ValueError("contagens inválidas")
    p = sucessos / n
    z = NormalDist().inv_cdf((1 + confianca) / 2)
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centro - h, centro + h
