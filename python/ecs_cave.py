"""Geração de cavernas por autômato celular com seed (1 = parede, 0 = chão)."""
from __future__ import annotations

import random

Grade = list[list[int]]


def _vizinhos_parede(g: Grade, x: int, y: int) -> int:
    h, w = len(g), len(g[0])
    n = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or g[ny][nx] == 1:
                n += 1  # fora do mapa conta como parede
    return n


def passo(g: Grade) -> Grade:
    """Regra 4-5: parede com >=4 vizinhas paredes permanece; chão vira parede com >=5."""
    h, w = len(g), len(g[0])
    novo = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            v = _vizinhos_parede(g, x, y)
            novo[y][x] = 1 if (v >= 4 if g[y][x] == 1 else v >= 5) else 0
    return novo


def componentes(g: Grade) -> list[list[tuple[int, int]]]:
    """Regiões de chão conexas (4-vizinhança), ordenadas da maior para a menor."""
    h, w = len(g), len(g[0])
    visto = [[False] * w for _ in range(h)]
    regioes = []
    for y in range(h):
        for x in range(w):
            if g[y][x] == 0 and not visto[y][x]:
                pilha, reg = [(x, y)], []
                visto[y][x] = True
                while pilha:
                    cx, cy = pilha.pop()
                    reg.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and g[ny][nx] == 0 and not visto[ny][nx]:
                            visto[ny][nx] = True
                            pilha.append((nx, ny))
                regioes.append(reg)
    regioes.sort(key=lambda r: (-len(r), min(r)))
    return regioes


def gerar(
    largura: int,
    altura: int,
    seed: int,
    prob_parede: float = 0.45,
    iteracoes: int = 4,
    manter_maior: bool = True,
) -> Grade:
    if largura < 3 or altura < 3:
        raise ValueError("mapa deve ter pelo menos 3x3")
    if not 0.0 <= prob_parede <= 1.0:
        raise ValueError("prob_parede fora de [0, 1]")
    rng = random.Random(seed)
    g = [
        [1 if x in (0, largura - 1) or y in (0, altura - 1) or rng.random() < prob_parede else 0
         for x in range(largura)]
        for y in range(altura)
    ]
    for _ in range(iteracoes):
        g = passo(g)
    if manter_maior:
        regs = componentes(g)
        for reg in regs[1:]:
            for x, y in reg:
                g[y][x] = 1
    return g
