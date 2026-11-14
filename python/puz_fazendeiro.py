"""Fazendeiro, lobo, cabra e couve: BFS sobre o espaço de estados."""
from __future__ import annotations

from collections import deque
from typing import Optional

# Estado: (fazendeiro, lobo, cabra, couve) com 0 = margem inicial, 1 = margem oposta.
Estado = tuple[int, int, int, int]
NOMES = ("lobo", "cabra", "couve")
INICIAL: Estado = (0, 0, 0, 0)
FINAL: Estado = (1, 1, 1, 1)


def seguro(e: Estado) -> bool:
    f, lobo, cabra, couve = e
    if lobo == cabra and f != cabra:
        return False
    if cabra == couve and f != cabra:
        return False
    return True


def sucessores(e: Estado) -> list[tuple[str, Estado]]:
    f = e[0]
    saida = []
    for i, nome in enumerate(NOMES, start=1):
        if e[i] == f:
            novo = list(e)
            novo[0] = novo[i] = 1 - f
            saida.append((nome, tuple(novo)))
    sozinho = list(e)
    sozinho[0] = 1 - f
    saida.append(("sozinho", tuple(sozinho)))
    return [(m, s) for m, s in saida if seguro(s)]


def resolver(inicial: Estado = INICIAL) -> Optional[list[str]]:
    """Menor lista de cargas transportadas a cada travessia, ou None."""
    if not seguro(inicial):
        return None
    fila = deque([inicial])
    pai: dict[Estado, Optional[tuple[Estado, str]]] = {inicial: None}
    while fila:
        atual = fila.popleft()
        if atual == FINAL:
            passos = []
            while pai[atual] is not None:
                atual, m = pai[atual]
                passos.append(m)
            return passos[::-1]
        for m, s in sucessores(atual):
            if s not in pai:
                pai[s] = (atual, m)
                fila.append(s)
    return None


def contar_estados_alcancaveis() -> int:
    vistos = {INICIAL}
    fila = deque([INICIAL])
    while fila:
        for _, s in sucessores(fila.popleft()):
            if s not in vistos:
                vistos.add(s)
                fila.append(s)
    return len(vistos)
