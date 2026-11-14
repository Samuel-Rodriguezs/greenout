"""Grafo não direcionado com BFS, DFS e caminho mais curto."""
from __future__ import annotations

from collections import deque
from typing import Dict, Hashable, List, Optional, Set


class Grafo:
    def __init__(self) -> None:
        self._adj: Dict[Hashable, List[Hashable]] = {}

    def adicionar_vertice(self, v: Hashable) -> None:
        self._adj.setdefault(v, [])

    def adicionar_aresta(self, a: Hashable, b: Hashable) -> None:
        self.adicionar_vertice(a)
        self.adicionar_vertice(b)
        if b not in self._adj[a]:
            self._adj[a].append(b)
        if a not in self._adj[b]:
            self._adj[b].append(a)

    def vertices(self) -> List[Hashable]:
        return list(self._adj)

    def vizinhos(self, v: Hashable) -> List[Hashable]:
        if v not in self._adj:
            raise KeyError(v)
        return list(self._adj[v])

    def bfs(self, origem: Hashable) -> List[Hashable]:
        if origem not in self._adj:
            raise KeyError(origem)
        visitados = {origem}
        fila = deque([origem])
        ordem: List[Hashable] = []
        while fila:
            v = fila.popleft()
            ordem.append(v)
            for w in self._adj[v]:
                if w not in visitados:
                    visitados.add(w)
                    fila.append(w)
        return ordem

    def dfs(self, origem: Hashable) -> List[Hashable]:
        if origem not in self._adj:
            raise KeyError(origem)
        visitados: Set[Hashable] = set()
        ordem: List[Hashable] = []
        pilha = [origem]
        while pilha:
            v = pilha.pop()
            if v in visitados:
                continue
            visitados.add(v)
            ordem.append(v)
            pilha.extend(reversed(self._adj[v]))
        return ordem

    def caminho_mais_curto(self, origem: Hashable, destino: Hashable) -> Optional[List[Hashable]]:
        """Menor caminho em número de arestas, ou None se inalcançável."""
        for v in (origem, destino):
            if v not in self._adj:
                raise KeyError(v)
        pai: Dict[Hashable, Optional[Hashable]] = {origem: None}
        fila = deque([origem])
        while fila:
            v = fila.popleft()
            if v == destino:
                caminho: List[Hashable] = []
                atual: Optional[Hashable] = v
                while atual is not None:
                    caminho.append(atual)
                    atual = pai[atual]
                return caminho[::-1]
            for w in self._adj[v]:
                if w not in pai:
                    pai[w] = v
                    fila.append(w)
        return None
