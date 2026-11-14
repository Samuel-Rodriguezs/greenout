"""Bellman-Ford: menores caminhos com pesos negativos e detecção de ciclo negativo."""

from __future__ import annotations

INF = float("inf")


class CicloNegativoError(Exception):
    """Levantada quando há ciclo de peso negativo alcançável da origem."""


def bellman_ford(
    vertices: list[str], arestas: list[tuple[str, str, float]], origem: str
) -> tuple[dict[str, float], dict[str, str | None]]:
    """Retorna (distâncias, predecessores) a partir da origem."""
    if origem not in vertices:
        raise ValueError("origem inexistente")
    dist: dict[str, float] = {v: INF for v in vertices}
    pred: dict[str, str | None] = {v: None for v in vertices}
    dist[origem] = 0
    for _ in range(len(vertices) - 1):
        mudou = False
        for u, v, p in arestas:
            if dist[u] != INF and dist[u] + p < dist[v]:
                dist[v] = dist[u] + p
                pred[v] = u
                mudou = True
        if not mudou:
            break
    for u, v, p in arestas:
        if dist[u] != INF and dist[u] + p < dist[v]:
            raise CicloNegativoError("ciclo negativo detectado")
    return dist, pred


def caminho(pred: dict[str, str | None], destino: str) -> list[str]:
    """Reconstrói o caminho até o destino a partir dos predecessores."""
    res: list[str] = []
    atual: str | None = destino
    while atual is not None:
        res.append(atual)
        atual = pred[atual]
    return res[::-1]
