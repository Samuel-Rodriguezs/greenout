"""Detecção de ciclo em grafos direcionados e não direcionados."""

from __future__ import annotations

from typing import Hashable


def ciclo_direcionado(grafo: dict[Hashable, list[Hashable]]) -> list[Hashable] | None:
    """Retorna um ciclo (lista de nós, primeiro == último) ou None."""
    BRANCO, CINZA, PRETO = 0, 1, 2
    cor: dict[Hashable, int] = {}
    pai: dict[Hashable, Hashable | None] = {}
    nos: list[Hashable] = list(grafo)
    for vs in grafo.values():
        nos.extend(vs)
    for raiz in nos:
        if cor.get(raiz, BRANCO) != BRANCO:
            continue
        cor[raiz] = CINZA
        pai[raiz] = None
        pilha = [(raiz, iter(grafo.get(raiz, [])))]
        while pilha:
            u, it = pilha[-1]
            for v in it:
                c = cor.get(v, BRANCO)
                if c == CINZA:
                    ciclo = [u]
                    while ciclo[-1] != v:
                        ciclo.append(pai[ciclo[-1]])  # type: ignore[arg-type]
                    ciclo.reverse()
                    ciclo.append(v)
                    return ciclo
                if c == BRANCO:
                    cor[v] = CINZA
                    pai[v] = u
                    pilha.append((v, iter(grafo.get(v, []))))
                    break
            else:
                cor[u] = PRETO
                pilha.pop()
    return None


def tem_ciclo_nao_direcionado(n: int, arestas: list[tuple[int, int]]) -> bool:
    """Usa union-find; auto-laços e arestas paralelas contam como ciclo."""
    pai = list(range(n))

    def achar(x: int) -> int:
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for u, v in arestas:
        ru, rv = achar(u), achar(v)
        if ru == rv:
            return True
        pai[ru] = rv
    return False
