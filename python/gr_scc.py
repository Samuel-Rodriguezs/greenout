"""Componentes fortemente conexos (Tarjan iterativo) em grafo direcionado."""

from __future__ import annotations

from typing import Hashable


def componentes_fortes(grafo: dict[Hashable, list[Hashable]]) -> list[list[Hashable]]:
    """Retorna as SCCs em ordem topológica reversa (Tarjan)."""
    nos: set[Hashable] = set(grafo)
    for vs in grafo.values():
        nos.update(vs)
    indice: dict[Hashable, int] = {}
    baixo: dict[Hashable, int] = {}
    na_pilha: set[Hashable] = set()
    pilha: list[Hashable] = []
    resultado: list[list[Hashable]] = []
    contador = 0

    for raiz in sorted(nos, key=repr):
        if raiz in indice:
            continue
        trabalho: list[tuple[Hashable, int]] = [(raiz, 0)]
        while trabalho:
            v, i = trabalho.pop()
            if i == 0:
                indice[v] = baixo[v] = contador
                contador += 1
                pilha.append(v)
                na_pilha.add(v)
            vizinhos = grafo.get(v, [])
            recursou = False
            while i < len(vizinhos):
                w = vizinhos[i]
                i += 1
                if w not in indice:
                    trabalho.append((v, i))
                    trabalho.append((w, 0))
                    recursou = True
                    break
                if w in na_pilha:
                    baixo[v] = min(baixo[v], indice[w])
            if recursou:
                continue
            if baixo[v] == indice[v]:
                comp: list[Hashable] = []
                while True:
                    w = pilha.pop()
                    na_pilha.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                resultado.append(comp)
            if trabalho:
                pai = trabalho[-1][0]
                baixo[pai] = min(baixo[pai], baixo[v])
    return resultado
