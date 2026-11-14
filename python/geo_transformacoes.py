"""Translação, rotação e escala por matrizes homogêneas 3x3."""
from __future__ import annotations

import math

Matriz = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
Ponto = tuple[float, float]

IDENTIDADE: Matriz = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def translacao(dx: float, dy: float) -> Matriz:
    return ((1, 0, dx), (0, 1, dy), (0, 0, 1))


def escala(sx: float, sy: float | None = None) -> Matriz:
    sy = sx if sy is None else sy
    return ((sx, 0, 0), (0, sy, 0), (0, 0, 1))


def rotacao(angulo: float) -> Matriz:
    """Rotação anti-horária em radianos em torno da origem."""
    c, s = math.cos(angulo), math.sin(angulo)
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def compor(*matrizes: Matriz) -> Matriz:
    """Produto M1 @ M2 @ ...; a última matriz é aplicada primeiro ao ponto."""
    res: Matriz = IDENTIDADE
    for m in matrizes:
        res = tuple(  # type: ignore[assignment]
            tuple(sum(res[i][k] * m[k][j] for k in range(3)) for j in range(3))
            for i in range(3)
        )
    return res


def rotacao_em_torno(angulo: float, centro: Ponto) -> Matriz:
    return compor(translacao(*centro), rotacao(angulo), translacao(-centro[0], -centro[1]))


def escala_em_torno(sx: float, sy: float, centro: Ponto) -> Matriz:
    return compor(translacao(*centro), escala(sx, sy), translacao(-centro[0], -centro[1]))


def aplicar(m: Matriz, p: Ponto) -> Ponto:
    x = m[0][0] * p[0] + m[0][1] * p[1] + m[0][2]
    y = m[1][0] * p[0] + m[1][1] * p[1] + m[1][2]
    w = m[2][0] * p[0] + m[2][1] * p[1] + m[2][2]
    if w == 0:
        raise ValueError("ponto no infinito")
    return (x / w, y / w)


def determinante(m: Matriz) -> float:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def inversa(m: Matriz) -> Matriz:
    d = determinante(m)
    if d == 0:
        raise ValueError("matriz singular")
    cof = [
        [
            (m[(j + 1) % 3][(i + 1) % 3] * m[(j + 2) % 3][(i + 2) % 3]
             - m[(j + 1) % 3][(i + 2) % 3] * m[(j + 2) % 3][(i + 1) % 3]) / d
            for j in range(3)
        ]
        for i in range(3)
    ]
    return tuple(tuple(r) for r in cof)  # type: ignore[return-value]
