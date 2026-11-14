"""Amostragem ponderada, com e sem reposição, e reservatório (reservoir sampling)."""
from __future__ import annotations

import math
import random
from itertools import accumulate
from bisect import bisect_right
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


def _validar_pesos(n: int, pesos: Sequence[float]) -> None:
    if len(pesos) != n:
        raise ValueError("pesos e itens devem ter o mesmo tamanho")
    if any(p < 0 or math.isnan(p) for p in pesos):
        raise ValueError("pesos não podem ser negativos")
    if sum(pesos) <= 0:
        raise ValueError("soma dos pesos deve ser positiva")


def com_reposicao(rng: random.Random, itens: Sequence[T], pesos: Sequence[float], k: int) -> list[T]:
    """k sorteios independentes, proporcionais aos pesos (busca binária nas somas acumuladas)."""
    _validar_pesos(len(itens), pesos)
    acum = list(accumulate(pesos))
    total = acum[-1]
    return [itens[bisect_right(acum, rng.random() * total)] for _ in range(k)]


def sem_reposicao(rng: random.Random, itens: Sequence[T], pesos: Sequence[float], k: int) -> list[T]:
    """k itens distintos (Efraimidis–Spirakis): chave u^(1/w), pegam-se as k maiores.

    Itens de peso zero só entram se não houver itens de peso positivo suficientes -> erro."""
    _validar_pesos(len(itens), pesos)
    positivos = sum(1 for p in pesos if p > 0)
    if k > positivos:
        raise ValueError("k maior que o número de itens com peso positivo")
    chaves = [
        (math.log(1.0 - rng.random()) / p, i) for i, p in enumerate(pesos) if p > 0
    ]  # log(u)/w é monotônico com u^(1/w); 1-random() evita log(0)
    chaves.sort(reverse=True)
    return [itens[i] for _, i in chaves[:k]]


def reservatorio(rng: random.Random, fluxo: Iterable[T], k: int) -> list[T]:
    """k itens uniformes de um fluxo de tamanho desconhecido (algoritmo R)."""
    if k < 0:
        raise ValueError("k deve ser >= 0")
    amostra: list[T] = []
    for i, x in enumerate(fluxo):
        if i < k:
            amostra.append(x)
        else:
            j = rng.randint(0, i)
            if j < k:
                amostra[j] = x
    return amostra
