"""Pontes e pontos de articulação em grafo não direcionado (DFS iterativo com low-link)."""

from __future__ import annotations


def pontes_e_articulacoes(
    n: int, arestas: list[tuple[int, int]]
) -> tuple[list[tuple[int, int]], set[int]]:
    """Retorna (pontes, articulações). Arestas paralelas nunca são pontes."""
    adj: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for i, (u, v) in enumerate(arestas):
        if u == v:
            continue
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    tempo = 0
    pontes: list[tuple[int, int]] = []
    artic: set[int] = set()
    for raiz in range(n):
        if tin[raiz] != -1:
            continue
        filhos_raiz = 0
        tin[raiz] = low[raiz] = tempo
        tempo += 1
        pilha = [(raiz, -1, 0)]  # (vértice, aresta do pai, próximo índice)
        while pilha:
            u, aresta_pai, i = pilha.pop()
            if i < len(adj[u]):
                pilha.append((u, aresta_pai, i + 1))
                v, e = adj[u][i]
                if e == aresta_pai:
                    continue
                if tin[v] == -1:
                    tin[v] = low[v] = tempo
                    tempo += 1
                    pilha.append((v, e, 0))
                else:
                    low[u] = min(low[u], tin[v])
            elif pilha:
                p = pilha[-1][0]
                low[p] = min(low[p], low[u])
                if low[u] > tin[p]:
                    pontes.append((min(p, u), max(p, u)))
                if p == raiz:
                    filhos_raiz += 1
                elif low[u] >= tin[p]:
                    artic.add(p)
        if filhos_raiz > 1:
            artic.add(raiz)
    return sorted(pontes), artic
