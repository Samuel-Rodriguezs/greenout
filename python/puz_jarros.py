"""Problema dos jarros de água: BFS sobre estados (quantidade em cada jarro)."""
from __future__ import annotations

from collections import deque
from math import gcd
from typing import Optional

Estado = tuple[int, ...]


def sucessores(estado: Estado, capacidades: tuple[int, ...]) -> list[tuple[str, Estado]]:
    saida: list[tuple[str, Estado]] = []
    n = len(capacidades)
    for i in range(n):
        if estado[i] < capacidades[i]:
            e = list(estado)
            e[i] = capacidades[i]
            saida.append((f"encher {i}", tuple(e)))
        if estado[i] > 0:
            e = list(estado)
            e[i] = 0
            saida.append((f"esvaziar {i}", tuple(e)))
        for j in range(n):
            if i != j and estado[i] > 0 and estado[j] < capacidades[j]:
                q = min(estado[i], capacidades[j] - estado[j])
                e = list(estado)
                e[i] -= q
                e[j] += q
                saida.append((f"despejar {i}->{j}", tuple(e)))
    return saida


def resolver(capacidades: tuple[int, ...], alvo: int) -> Optional[list[str]]:
    """Menor sequência de operações para algum jarro conter exatamente `alvo` litros."""
    if alvo < 0 or any(c <= 0 for c in capacidades):
        raise ValueError("capacidades e alvo devem ser positivos")
    if alvo > max(capacidades):
        return None
    inicial: Estado = (0,) * len(capacidades)
    pai: dict[Estado, Optional[tuple[Estado, str]]] = {inicial: None}
    fila = deque([inicial])
    while fila:
        atual = fila.popleft()
        if alvo in atual:
            passos = []
            while pai[atual] is not None:
                atual, op = pai[atual]
                passos.append(op)
            return passos[::-1]
        for op, s in sucessores(atual, capacidades):
            if s not in pai:
                pai[s] = (atual, op)
                fila.append(s)
    return None


def possivel_dois_jarros(a: int, b: int, alvo: int) -> bool:
    """Critério de Bézout: alvo <= max e múltiplo de mdc(a, b)."""
    return alvo <= max(a, b) and alvo % gcd(a, b) == 0
