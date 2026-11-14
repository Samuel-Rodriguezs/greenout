"""Fecho convexo: monotone chain (Andrew) e varredura de Graham.

Ambos devolvem os vértices em ordem anti-horária, sem pontos colineares nas
arestas e sem duplicatas.
"""
from __future__ import annotations

import math
from functools import cmp_to_key

from geo_orientacao import orientacao

Ponto = tuple[float, float]


def andrew(pontos: list[Ponto]) -> list[Ponto]:
    pts = sorted(set(pontos))
    if len(pts) <= 2:
        return pts

    def metade(seq: list[Ponto]) -> list[Ponto]:
        cadeia: list[Ponto] = []
        for p in seq:
            while len(cadeia) >= 2 and orientacao(cadeia[-2], cadeia[-1], p) <= 0:
                cadeia.pop()
            cadeia.append(p)
        return cadeia

    inferior = metade(pts)
    superior = metade(pts[::-1])
    return inferior[:-1] + superior[:-1]


def graham(pontos: list[Ponto]) -> list[Ponto]:
    pts = sorted(set(pontos), key=lambda p: (p[1], p[0]))
    if len(pts) <= 2:
        return sorted(pts)
    base = pts[0]
    resto = pts[1:]

    def cmp(a: Ponto, b: Ponto) -> int:
        o = orientacao(base, a, b)
        if o != 0:
            return -o  # anti-horário primeiro
        da = math.dist(base, a)
        db = math.dist(base, b)
        return (da > db) - (da < db)  # colineares: mais perto primeiro

    resto.sort(key=cmp_to_key(cmp))
    pilha = [base]
    for p in resto:
        while len(pilha) >= 2 and orientacao(pilha[-2], pilha[-1], p) <= 0:
            pilha.pop()
        pilha.append(p)
    # na última direção (aresta de fechamento) sobram colineares intermediários
    while len(pilha) >= 3 and orientacao(base, pilha[-2], pilha[-1]) == 0:
        del pilha[-2]
    return sorted(pilha) if len(pilha) == 2 else pilha
