"""Simulação de Monte Carlo de preços (movimento browniano geométrico) com seed."""
from __future__ import annotations

import math
import random


def simular_caminhos(
    s0: float,
    mu: float,
    sigma: float,
    t: float,
    passos: int,
    n_caminhos: int,
    seed: int = 0,
) -> list[list[float]]:
    """Cada caminho tem passos+1 pontos: S(t+dt) = S(t)*exp((mu-s²/2)dt + s*sqrt(dt)*Z)."""
    if s0 <= 0 or sigma < 0 or t <= 0 or passos <= 0 or n_caminhos <= 0:
        raise ValueError("parâmetros inválidos")
    rng = random.Random(seed)
    dt = t / passos
    deriva = (mu - sigma**2 / 2) * dt
    difusao = sigma * math.sqrt(dt)
    caminhos: list[list[float]] = []
    for _ in range(n_caminhos):
        caminho = [s0]
        for _ in range(passos):
            caminho.append(caminho[-1] * math.exp(deriva + difusao * rng.gauss(0.0, 1.0)))
        caminhos.append(caminho)
    return caminhos


def preco_opcao_mc(
    s0: float,
    k: float,
    r: float,
    sigma: float,
    t: float,
    n_caminhos: int,
    tipo: str = "call",
    seed: int = 0,
) -> tuple[float, float]:
    """Opção europeia sob medida neutra ao risco, com variáveis antitéticas.
    Devolve (preço estimado, erro-padrão)."""
    if tipo not in ("call", "put"):
        raise ValueError("tipo deve ser 'call' ou 'put'")
    if s0 <= 0 or k <= 0 or sigma < 0 or t <= 0 or n_caminhos <= 0:
        raise ValueError("parâmetros inválidos")
    rng = random.Random(seed)
    sinal = 1 if tipo == "call" else -1
    deriva = (r - sigma**2 / 2) * t
    difusao = sigma * math.sqrt(t)
    pares: list[float] = []
    for _ in range(n_caminhos):
        z = rng.gauss(0.0, 1.0)
        pagamentos = (
            max(sinal * (s0 * math.exp(deriva + difusao * zz) - k), 0.0) for zz in (z, -z)
        )
        pares.append(sum(pagamentos) / 2)
    media = sum(pares) / n_caminhos
    desconto = math.exp(-r * t)
    if n_caminhos > 1:
        var = sum((x - media) ** 2 for x in pares) / (n_caminhos - 1)
        erro = desconto * math.sqrt(var / n_caminhos)
    else:
        erro = 0.0
    return desconto * media, erro
