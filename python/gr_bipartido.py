"""Teste de bipartição por BFS."""

from __future__ import annotations

from collections import deque
from typing import Hashable


def bipartir(grafo: dict[Hashable, list[Hashable]]) -> tuple[set[Hashable], set[Hashable]] | None:
    """Retorna as duas partes ou None se o grafo (não direcionado) não é bipartido."""
    adj: dict[Hashable, set[Hashable]] = {}
    for u, vs in grafo.items():
        adj.setdefault(u, set())
        for v in vs:
            adj[u].add(v)
            adj.setdefault(v, set()).add(u)
    lado: dict[Hashable, int] = {}
    for raiz in sorted(adj, key=repr):
        if raiz in lado:
            continue
        lado[raiz] = 0
        fila = deque([raiz])
        while fila:
            u = fila.popleft()
            for v in adj[u]:
                if v not in lado:
                    lado[v] = 1 - lado[u]
                    fila.append(v)
                elif lado[v] == lado[u]:
                    return None
    return ({v for v, s in lado.items() if s == 0}, {v for v, s in lado.items() if s == 1})


def eh_bipartido(grafo: dict[Hashable, list[Hashable]]) -> bool:
    return bipartir(grafo) is not None
