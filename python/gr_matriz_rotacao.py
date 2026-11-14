"""Rotação de matriz e percurso em espiral."""

from __future__ import annotations

Matriz = list[list[int]]


def _validar(m: Matriz) -> None:
    if m and any(len(l) != len(m[0]) for l in m):
        raise ValueError("matriz irregular")


def rotacionar_90(m: Matriz) -> Matriz:
    """Nova matriz girada 90 graus no sentido horário (aceita retangulares)."""
    _validar(m)
    return [list(l) for l in zip(*m[::-1])]


def rotacionar_antihorario(m: Matriz) -> Matriz:
    _validar(m)
    return [list(l) for l in zip(*m)][::-1]


def rotacionar_in_place(m: Matriz) -> None:
    """Gira 90 graus horário in-place; exige matriz quadrada."""
    n = len(m)
    if any(len(l) != n for l in m):
        raise ValueError("matriz deve ser quadrada")
    for i in range(n // 2):
        for j in range(i, n - 1 - i):
            m[i][j], m[j][n - 1 - i], m[n - 1 - i][n - 1 - j], m[n - 1 - j][i] = (
                m[n - 1 - j][i],
                m[i][j],
                m[j][n - 1 - i],
                m[n - 1 - i][n - 1 - j],
            )


def espiral(m: Matriz) -> list[int]:
    """Elementos em ordem espiral horária a partir do canto superior esquerdo."""
    _validar(m)
    if not m or not m[0]:
        return []
    topo, base, esq, dir = 0, len(m) - 1, 0, len(m[0]) - 1
    res: list[int] = []
    while topo <= base and esq <= dir:
        res.extend(m[topo][esq:dir + 1])
        res.extend(m[i][dir] for i in range(topo + 1, base + 1))
        if topo < base:
            res.extend(m[base][j] for j in range(dir - 1, esq - 1, -1))
        if esq < dir:
            res.extend(m[i][esq] for i in range(base - 1, topo, -1))
        topo, base, esq, dir = topo + 1, base - 1, esq + 1, dir - 1
    return res
