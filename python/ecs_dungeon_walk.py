"""Geração de cavernas por random walk (drunkard's walk) com seed (1 = parede, 0 = chão)."""
from __future__ import annotations

import random

Grade = list[list[int]]

_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def gerar(
    largura: int,
    altura: int,
    seed: int,
    fracao_chao: float = 0.4,
    persistencia: float = 0.0,
    max_passos: int = 1_000_000,
) -> tuple[Grade, list[tuple[int, int]]]:
    """Um caminhante parte do centro e escava até atingir `fracao_chao` do interior.

    `persistencia` (0..1) é a chance de repetir a direção anterior, gerando
    túneis mais longos. Devolve (grade, ordem em que as células foram escavadas).
    """
    if largura < 5 or altura < 5:
        raise ValueError("mapa deve ter pelo menos 5x5")
    if not 0.0 < fracao_chao <= 1.0:
        raise ValueError("fracao_chao deve estar em (0, 1]")
    if not 0.0 <= persistencia <= 1.0:
        raise ValueError("persistencia fora de [0, 1]")
    rng = random.Random(seed)
    g: Grade = [[1] * largura for _ in range(altura)]
    alvo = max(1, round((largura - 2) * (altura - 2) * fracao_chao))
    x, y = largura // 2, altura // 2
    g[y][x] = 0
    ordem = [(x, y)]
    d = rng.choice(_DIRS)
    for _ in range(max_passos):
        if len(ordem) >= alvo:
            break
        if rng.random() >= persistencia:
            d = rng.choice(_DIRS)
        nx, ny = x + d[0], y + d[1]
        if not (1 <= nx < largura - 1 and 1 <= ny < altura - 1):
            d = rng.choice(_DIRS)
            continue
        x, y = nx, ny
        if g[y][x] == 1:
            g[y][x] = 0
            ordem.append((x, y))
    return g, ordem
