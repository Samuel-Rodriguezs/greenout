"""Opção por árvore binomial de Cox-Ross-Rubinstein (europeia ou americana)."""
from __future__ import annotations

import math


def preco_binomial(
    s: float,
    k: float,
    r: float,
    sigma: float,
    t: float,
    passos: int,
    tipo: str = "call",
    americana: bool = False,
) -> float:
    if tipo not in ("call", "put"):
        raise ValueError("tipo deve ser 'call' ou 'put'")
    if s <= 0 or k <= 0 or sigma <= 0 or t <= 0 or passos <= 0:
        raise ValueError("s, k, sigma, t e passos devem ser positivos")
    dt = t / passos
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d) / (u - d)
    if not 0 <= p <= 1:
        raise ValueError("árvore com arbitragem: aumente os passos ou ajuste r/sigma")
    desconto = math.exp(-r * dt)
    sinal = 1 if tipo == "call" else -1

    def payoff(preco: float) -> float:
        return max(sinal * (preco - k), 0.0)

    valores = [payoff(s * u ** (passos - j) * d**j) for j in range(passos + 1)]
    for n in range(passos - 1, -1, -1):
        for j in range(n + 1):
            v = desconto * (p * valores[j] + (1 - p) * valores[j + 1])
            if americana:
                v = max(v, payoff(s * u ** (n - j) * d**j))
            valores[j] = v
    return valores[0]
