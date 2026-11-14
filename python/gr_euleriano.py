"""Caminho/circuito euleriano em grafo não direcionado (Hierholzer)."""

from __future__ import annotations

from collections import defaultdict
from typing import Hashable


def caminho_euleriano(arestas: list[tuple[Hashable, Hashable]]) -> list[Hashable] | None:
    """Retorna sequência de vértices que usa cada aresta uma vez, ou None se inexistente."""
    if not arestas:
        return []
    adj: dict[Hashable, list[tuple[Hashable, int]]] = defaultdict(list)
    for i, (u, v) in enumerate(arestas):
        adj[u].append((v, i))
        adj[v].append((u, i))
    impares = [v for v in adj if len(adj[v]) % 2]
    if len(impares) not in (0, 2):
        return None
    inicio = impares[0] if impares else next(iter(adj))
    usada = [False] * len(arestas)
    pilha = [inicio]
    caminho: list[Hashable] = []
    while pilha:
        u = pilha[-1]
        while adj[u] and usada[adj[u][-1][1]]:
            adj[u].pop()
        if adj[u]:
            v, i = adj[u].pop()
            usada[i] = True
            pilha.append(v)
        else:
            caminho.append(pilha.pop())
    if len(caminho) != len(arestas) + 1:
        return None  # grafo desconexo
    return caminho[::-1]
