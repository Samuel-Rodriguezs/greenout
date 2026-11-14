"""Opção europeia por Black-Scholes-Merton: preço, gregas e volatilidade implícita."""
from __future__ import annotations

import math
from statistics import NormalDist

_N = NormalDist()


def _d1_d2(s: float, k: float, r: float, sigma: float, t: float) -> tuple[float, float]:
    d1 = (math.log(s / k) + (r + sigma**2 / 2) * t) / (sigma * math.sqrt(t))
    return d1, d1 - sigma * math.sqrt(t)


def _validar(s: float, k: float, sigma: float, t: float) -> None:
    if s <= 0 or k <= 0:
        raise ValueError("S e K devem ser positivos")
    if sigma < 0 or t < 0:
        raise ValueError("sigma e T não podem ser negativos")


def preco_call(s: float, k: float, r: float, sigma: float, t: float, q: float = 0.0) -> float:
    """Preço da call europeia; q é o dividend yield contínuo."""
    _validar(s, k, sigma, t)
    if t == 0 or sigma == 0:
        # sem incerteza: valor descontado do payoff do forward
        fwd = s * math.exp(-q * t) - k * math.exp(-r * t)
        return max(fwd, 0.0)
    d1, d2 = _d1_d2(s * math.exp(-q * t), k, r, sigma, t)
    return s * math.exp(-q * t) * _N.cdf(d1) - k * math.exp(-r * t) * _N.cdf(d2)


def preco_put(s: float, k: float, r: float, sigma: float, t: float, q: float = 0.0) -> float:
    _validar(s, k, sigma, t)
    if t == 0 or sigma == 0:
        fwd = k * math.exp(-r * t) - s * math.exp(-q * t)
        return max(fwd, 0.0)
    d1, d2 = _d1_d2(s * math.exp(-q * t), k, r, sigma, t)
    return k * math.exp(-r * t) * _N.cdf(-d2) - s * math.exp(-q * t) * _N.cdf(-d1)


def gregas(s: float, k: float, r: float, sigma: float, t: float, tipo: str = "call") -> dict[str, float]:
    """Delta, gamma e vega (por 1.00 de volatilidade) sem dividendos."""
    if tipo not in ("call", "put"):
        raise ValueError("tipo deve ser 'call' ou 'put'")
    _validar(s, k, sigma, t)
    if sigma == 0 or t == 0:
        raise ValueError("gregas exigem sigma > 0 e T > 0")
    d1, _ = _d1_d2(s, k, r, sigma, t)
    delta = _N.cdf(d1) if tipo == "call" else _N.cdf(d1) - 1
    gamma = _N.pdf(d1) / (s * sigma * math.sqrt(t))
    vega = s * _N.pdf(d1) * math.sqrt(t)
    return {"delta": delta, "gamma": gamma, "vega": vega}


def volatilidade_implicita(
    preco: float, s: float, k: float, r: float, t: float, tipo: str = "call"
) -> float:
    """Resolve sigma por bisseção em [1e-6, 5]."""
    f = preco_call if tipo == "call" else preco_put
    if tipo not in ("call", "put"):
        raise ValueError("tipo deve ser 'call' ou 'put'")
    baixo, alto = 1e-6, 5.0
    if not f(s, k, r, baixo, t) <= preco <= f(s, k, r, alto, t):
        raise ValueError("preço fora do intervalo alcançável")
    for _ in range(200):
        meio = (baixo + alto) / 2
        if f(s, k, r, meio, t) < preco:
            baixo = meio
        else:
            alto = meio
    return (baixo + alto) / 2
