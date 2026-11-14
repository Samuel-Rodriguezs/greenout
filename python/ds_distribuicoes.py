"""Distribuições: normal (pdf/cdf/ppf), binomial e Poisson."""
from __future__ import annotations

import math
from statistics import NormalDist


def normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        raise ValueError("sigma deve ser positivo")
    z = (x - mu) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2 * math.pi))


def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        raise ValueError("sigma deve ser positivo")
    return 0.5 * math.erfc(-(x - mu) / (sigma * math.sqrt(2)))


def normal_ppf(p: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if not 0 < p < 1:
        raise ValueError("p deve estar em (0, 1)")
    return NormalDist(mu, sigma).inv_cdf(p)


def binomial_pmf(k: int, n: int, p: float) -> float:
    if n < 0 or not 0 <= p <= 1:
        raise ValueError("parâmetros inválidos")
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def binomial_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    return min(1.0, sum(binomial_pmf(i, n, p) for i in range(0, min(k, n) + 1)))


def poisson_pmf(k: int, lam: float) -> float:
    if lam < 0:
        raise ValueError("lambda deve ser não negativo")
    if k < 0:
        return 0.0
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def poisson_cdf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    return min(1.0, sum(poisson_pmf(i, lam) for i in range(0, k + 1)))


def binomial_media_variancia(n: int, p: float) -> tuple[float, float]:
    return n * p, n * p * (1 - p)
