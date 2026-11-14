"""Ranking com tratamento de empates (médio, mínimo, máximo, denso, ordinal)."""
from __future__ import annotations

from typing import Sequence

METODOS = ("medio", "minimo", "maximo", "denso", "ordinal")


def ranking(dados: Sequence[float], metodo: str = "medio", decrescente: bool = False) -> list[float]:
    """Posto de cada elemento (1 = menor, ou maior se decrescente)."""
    if metodo not in METODOS:
        raise ValueError(f"método deve ser um de {METODOS}")
    ordem = sorted(range(len(dados)), key=lambda i: dados[i], reverse=decrescente)
    if metodo == "ordinal":
        # sort é estável; em decrescente a estabilidade preserva a ordem original dos empates
        postos = [0.0] * len(dados)
        for r, i in enumerate(ordem, start=1):
            postos[i] = float(r)
        return postos
    postos = [0.0] * len(dados)
    i = 0
    denso = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and dados[ordem[j + 1]] == dados[ordem[i]]:
            j += 1
        denso += 1
        if metodo == "medio":
            valor = (i + j) / 2 + 1
        elif metodo == "minimo":
            valor = i + 1
        elif metodo == "maximo":
            valor = j + 1
        else:
            valor = denso
        for k in range(i, j + 1):
            postos[ordem[k]] = float(valor)
        i = j + 1
    return postos


def top_n(itens: Sequence[tuple[str, float]], n: int) -> list[tuple[int, str, float]]:
    """Os n maiores como (posição competitiva, nome, valor); empates dividem a posição."""
    if n < 0:
        raise ValueError("n deve ser não negativo")
    ordenado = sorted(itens, key=lambda t: (-t[1], t[0]))
    pos = ranking([v for _, v in ordenado], "minimo", decrescente=True)
    return [(int(pos[k]), nome, valor) for k, (nome, valor) in enumerate(ordenado[:n])]
