"""Raycast em grade 2D pelo algoritmo DDA (Amanatides & Woo)."""
from __future__ import annotations

from dataclasses import dataclass
from math import floor, hypot, inf
from typing import Callable


@dataclass(frozen=True)
class Acerto:
    celula: tuple[int, int]
    distancia: float
    ponto: tuple[float, float]
    normal: tuple[int, int]  # face atingida (aponta para fora da célula, de volta ao raio)


def percorrer(
    origem: tuple[float, float],
    direcao: tuple[float, float],
    distancia_max: float,
) -> list[tuple[tuple[int, int], float]]:
    """Células (i, j) atravessadas e distância de entrada em cada uma. Células de lado 1."""
    dx, dy = direcao
    norma = hypot(dx, dy)
    if norma == 0:
        raise ValueError("direção nula")
    dx, dy = dx / norma, dy / norma
    ox, oy = origem
    i, j = floor(ox), floor(oy)
    passo_i = 1 if dx > 0 else -1
    passo_j = 1 if dy > 0 else -1
    delta_x = abs(1 / dx) if dx else inf
    delta_y = abs(1 / dy) if dy else inf
    if dx > 0:
        t_x = (i + 1 - ox) * delta_x
    elif dx < 0:
        t_x = (ox - i) * delta_x
    else:
        t_x = inf
    if dy > 0:
        t_y = (j + 1 - oy) * delta_y
    elif dy < 0:
        t_y = (oy - j) * delta_y
    else:
        t_y = inf
    visitadas = [((i, j), 0.0)]
    while True:
        if t_x < t_y:
            t = t_x
            i += passo_i
            t_x += delta_x
        else:
            t = t_y
            j += passo_j
            t_y += delta_y
        if t > distancia_max or t == inf:
            return visitadas
        visitadas.append(((i, j), t))


def raycast(
    origem: tuple[float, float],
    direcao: tuple[float, float],
    distancia_max: float,
    bloqueada: Callable[[int, int], bool],
) -> Acerto | None:
    """Primeira célula bloqueada ao longo do raio, ou None.

    Se a origem já está dentro de uma célula bloqueada, o acerto tem distância 0.
    """
    norma = hypot(*direcao)
    if norma == 0:
        raise ValueError("direção nula")
    ux, uy = direcao[0] / norma, direcao[1] / norma
    anterior: tuple[int, int] | None = None
    for (i, j), t in percorrer(origem, direcao, distancia_max):
        if bloqueada(i, j):
            normal = (0, 0) if anterior is None else (anterior[0] - i, anterior[1] - j)
            return Acerto((i, j), t, (origem[0] + ux * t, origem[1] + uy * t), normal)
        anterior = (i, j)
    return None
