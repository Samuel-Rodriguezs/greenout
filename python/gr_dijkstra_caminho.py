"""Dijkstra com heapq e reconstrução do caminho."""

from __future__ import annotations

import heapq
from typing import Hashable

Grafo = dict[Hashable, list[tuple[Hashable, float]]]


def dijkstra(grafo: Grafo, origem: Hashable) -> tuple[dict[Hashable, float], dict[Hashable, Hashable]]:
    """Distâncias mínimas e mapa de predecessores a partir da origem."""
    for vizinhos in grafo.values():
        for _, p in vizinhos:
            if p < 0:
                raise ValueError("Dijkstra não aceita pesos negativos")
    dist: dict[Hashable, float] = {origem: 0}
    pred: dict[Hashable, Hashable] = {}
    heap: list[tuple[float, int, Hashable]] = [(0, 0, origem)]
    desempate = 1
    while heap:
        d, _, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        for v, p in grafo.get(u, []):
            nd = d + p
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, desempate, v))
                desempate += 1
    return dist, pred


def menor_caminho(grafo: Grafo, origem: Hashable, destino: Hashable) -> tuple[float, list[Hashable]] | None:
    """(custo, caminho) ou None se destino inalcançável."""
    dist, pred = dijkstra(grafo, origem)
    if destino not in dist:
        return None
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(pred[caminho[-1]])
    return dist[destino], caminho[::-1]
