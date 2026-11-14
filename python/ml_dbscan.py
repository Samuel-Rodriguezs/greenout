"""DBSCAN: agrupamento por densidade. Ruído recebe o rótulo -1."""
from __future__ import annotations

import math

RUIDO = -1


def dbscan(X: list[list[float]], eps: float, min_pts: int) -> list[int]:
    if eps <= 0 or min_pts < 1:
        raise ValueError("eps deve ser > 0 e min_pts >= 1")
    n = len(X)
    rotulos: list[int | None] = [None] * n

    def vizinhos(i: int) -> list[int]:
        return [j for j in range(n) if math.dist(X[i], X[j]) <= eps]

    cluster = 0
    for i in range(n):
        if rotulos[i] is not None:
            continue
        viz = vizinhos(i)
        if len(viz) < min_pts:
            rotulos[i] = RUIDO
            continue
        rotulos[i] = cluster
        fila = [j for j in viz if j != i]
        while fila:
            j = fila.pop()
            if rotulos[j] == RUIDO:
                rotulos[j] = cluster
            if rotulos[j] is not None:
                continue
            rotulos[j] = cluster
            viz_j = vizinhos(j)
            if len(viz_j) >= min_pts:
                fila.extend(viz_j)
        cluster += 1
    return [r if r is not None else RUIDO for r in rotulos]
