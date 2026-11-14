"""Grafos aleatórios não direcionados: Erdős–Rényi G(n, p) e Barabási–Albert."""
from __future__ import annotations

import random
from collections import deque

Aresta = tuple[int, int]


def erdos_renyi(rng: random.Random, n: int, p: float) -> list[Aresta]:
    """Cada par (u < v) vira aresta com probabilidade p. Vértices 0..n-1."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p deve estar em [0, 1]")
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


def barabasi_albert(rng: random.Random, n: int, m: int) -> list[Aresta]:
    """Ligação preferencial: começa com m+1 vértices em clique; cada novo liga-se a m existentes."""
    if m < 1 or n <= m:
        raise ValueError("exige 1 <= m < n")
    arestas: list[Aresta] = [(u, v) for u in range(m + 1) for v in range(u + 1, m + 1)]
    # lista de extremidades: grau de v = nº de ocorrências de v (amostragem proporcional ao grau)
    extremidades: list[int] = [x for a in arestas for x in a]
    for novo in range(m + 1, n):
        alvos: set[int] = set()
        while len(alvos) < m:
            alvos.add(rng.choice(extremidades))
        for alvo in sorted(alvos):
            arestas.append((alvo, novo))
            extremidades.extend((alvo, novo))
    return arestas


def graus(n: int, arestas: list[Aresta]) -> list[int]:
    g = [0] * n
    for u, v in arestas:
        g[u] += 1
        g[v] += 1
    return g


def lista_adjacencia(n: int, arestas: list[Aresta]) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in arestas:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def componentes_conexas(n: int, arestas: list[Aresta]) -> int:
    adj = lista_adjacencia(n, arestas)
    visto = [False] * n
    total = 0
    for s in range(n):
        if visto[s]:
            continue
        total += 1
        visto[s] = True
        fila = deque([s])
        while fila:
            u = fila.popleft()
            for w in adj[u]:
                if not visto[w]:
                    visto[w] = True
                    fila.append(w)
    return total
