"""Par de pontos mais próximo por divisão e conquista, O(n log n)."""
from __future__ import annotations

import math

Ponto = tuple[float, float]
Resultado = tuple[float, Ponto, Ponto]


def par_mais_proximo(pontos: list[Ponto]) -> Resultado:
    """Devolve (distância, p, q). Exige ao menos dois pontos."""
    if len(pontos) < 2:
        raise ValueError("são necessários ao menos dois pontos")
    por_x = sorted(pontos)
    por_y = sorted(pontos, key=lambda p: (p[1], p[0]))
    return _resolver(por_x, por_y)


def par_mais_proximo_forca_bruta(pontos: list[Ponto]) -> Resultado:
    if len(pontos) < 2:
        raise ValueError("são necessários ao menos dois pontos")
    melhor: Resultado | None = None
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            d = math.dist(pontos[i], pontos[j])
            if melhor is None or d < melhor[0]:
                melhor = (d, pontos[i], pontos[j])
    assert melhor is not None
    return melhor


def _resolver(por_x: list[Ponto], por_y: list[Ponto]) -> Resultado:
    n = len(por_x)
    if n <= 3:
        return par_mais_proximo_forca_bruta(por_x)
    meio = n // 2
    x_meio = por_x[meio][0]
    esquerda_x, direita_x = por_x[:meio], por_x[meio:]
    # particiona por_y mantendo a ordem; duplicatas são resolvidas por contagem
    esquerda_y: list[Ponto] = []
    direita_y: list[Ponto] = []
    restantes_esq = {}
    for p in esquerda_x:
        restantes_esq[p] = restantes_esq.get(p, 0) + 1
    for p in por_y:
        if restantes_esq.get(p, 0) > 0:
            restantes_esq[p] -= 1
            esquerda_y.append(p)
        else:
            direita_y.append(p)
    melhor = min(_resolver(esquerda_x, esquerda_y), _resolver(direita_x, direita_y))
    d = melhor[0]
    faixa = [p for p in por_y if abs(p[0] - x_meio) < d]
    for i in range(len(faixa)):
        j = i + 1
        while j < len(faixa) and faixa[j][1] - faixa[i][1] < d:
            dist = math.dist(faixa[i], faixa[j])
            if dist < d:
                d = dist
                melhor = (dist, faixa[i], faixa[j])
            j += 1
    return melhor
