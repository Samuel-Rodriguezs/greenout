"""Floyd-Warshall: menores caminhos entre todos os pares."""

from __future__ import annotations

INF = float("inf")


def floyd_warshall(
    n: int, arestas: list[tuple[int, int, float]]
) -> tuple[list[list[float]], list[list[int | None]]]:
    """Retorna matriz de distâncias e matriz 'próximo' para reconstruir caminhos."""
    if n < 0:
        raise ValueError("n inválido")
    dist = [[INF] * n for _ in range(n)]
    prox: list[list[int | None]] = [[None] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        prox[i][i] = i
    for u, v, p in arestas:
        if p < dist[u][v]:
            dist[u][v] = p
            prox[u][v] = v
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    prox[i][j] = prox[i][k]
    return dist, prox


def tem_ciclo_negativo(dist: list[list[float]]) -> bool:
    return any(dist[i][i] < 0 for i in range(len(dist)))


def reconstruir(prox: list[list[int | None]], u: int, v: int) -> list[int]:
    """Caminho de u a v; lista vazia se inalcançável."""
    if prox[u][v] is None:
        return []
    res = [u]
    while u != v:
        u = prox[u][v]  # type: ignore[assignment]
        res.append(u)
    return res
