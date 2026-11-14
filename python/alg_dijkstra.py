"""Menor caminho com o algoritmo de Dijkstra."""

import heapq


def dijkstra(grafo: dict[str, dict[str, float]], origem: str) -> dict[str, float]:
    """Distância mínima da origem a cada nó alcançável. Pesos não podem ser negativos."""
    if origem not in grafo:
        raise KeyError(f"origem inexistente: {origem}")
    distancias: dict[str, float] = {origem: 0}
    fila = [(0, origem)]
    while fila:
        dist, no = heapq.heappop(fila)
        if dist > distancias.get(no, float("inf")):
            continue
        for vizinho, peso in grafo.get(no, {}).items():
            if peso < 0:
                raise ValueError("pesos negativos não são suportados")
            nova = dist + peso
            if nova < distancias.get(vizinho, float("inf")):
                distancias[vizinho] = nova
                heapq.heappush(fila, (nova, vizinho))
    return distancias
