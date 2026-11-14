"""Árvore geradora mínima: Kruskal e Prim."""

from __future__ import annotations

import heapq


def kruskal(n: int, arestas: list[tuple[int, int, float]]) -> tuple[float, list[tuple[int, int, float]]]:
    """Floresta geradora mínima de um grafo não direcionado com n vértices (0..n-1)."""
    pai = list(range(n))

    def achar(x: int) -> int:
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    escolhidas: list[tuple[int, int, float]] = []
    total = 0.0
    for u, v, p in sorted(arestas, key=lambda a: a[2]):
        ru, rv = achar(u), achar(v)
        if ru != rv:
            pai[ru] = rv
            escolhidas.append((u, v, p))
            total += p
    return total, escolhidas


def prim(n: int, arestas: list[tuple[int, int, float]], inicio: int = 0) -> float:
    """Peso da MST da componente de `inicio`; ValueError se o grafo é desconexo."""
    if n == 0:
        return 0.0
    adj: list[list[tuple[float, int]]] = [[] for _ in range(n)]
    for u, v, p in arestas:
        adj[u].append((p, v))
        adj[v].append((p, u))
    visto = [False] * n
    heap = [(0.0, inicio)]
    total = 0.0
    contados = 0
    while heap:
        p, u = heapq.heappop(heap)
        if visto[u]:
            continue
        visto[u] = True
        total += p
        contados += 1
        for q, v in adj[u]:
            if not visto[v]:
                heapq.heappush(heap, (q, v))
    if contados != n:
        raise ValueError("grafo desconexo")
    return total
