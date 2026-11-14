"""Coloração gulosa de grafos (ordem por grau decrescente - Welsh-Powell)."""

from __future__ import annotations

from typing import Hashable


def colorir(grafo: dict[Hashable, list[Hashable]]) -> dict[Hashable, int]:
    """Atribui cores 0..k a cada vértice sem vizinhos com a mesma cor (grafo não direcionado)."""
    adj: dict[Hashable, set[Hashable]] = {v: set() for v in grafo}
    for u, vs in grafo.items():
        for v in vs:
            if u == v:
                raise ValueError("auto-laço impede coloração")
            adj[u].add(v)
            adj.setdefault(v, set()).add(u)
    ordem = sorted(adj, key=lambda v: (-len(adj[v]), repr(v)))
    cor: dict[Hashable, int] = {}
    for v in ordem:
        usadas = {cor[w] for w in adj[v] if w in cor}
        c = 0
        while c in usadas:
            c += 1
        cor[v] = c
    return cor


def numero_cores(cor: dict[Hashable, int]) -> int:
    return max(cor.values()) + 1 if cor else 0


def coloracao_valida(grafo: dict[Hashable, list[Hashable]], cor: dict[Hashable, int]) -> bool:
    return all(cor[u] != cor[v] for u, vs in grafo.items() for v in vs)
