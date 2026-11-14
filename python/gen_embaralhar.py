"""Embaralhamentos (Fisher–Yates), permutações aleatórias e partições de listas."""
from __future__ import annotations

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def fisher_yates(rng: random.Random, itens: Sequence[T]) -> list[T]:
    """Cópia embaralhada com distribuição uniforme sobre as n! permutações."""
    a = list(itens)
    for i in range(len(a) - 1, 0, -1):
        j = rng.randint(0, i)
        a[i], a[j] = a[j], a[i]
    return a


def permutacao_aleatoria(rng: random.Random, n: int) -> list[int]:
    return fisher_yates(rng, range(n))


def desarranjo(rng: random.Random, n: int) -> list[int]:
    """Permutação sem pontos fixos (rejeição); exige n != 1."""
    if n == 1:
        raise ValueError("não existe desarranjo de 1 elemento")
    while True:
        p = permutacao_aleatoria(rng, n)
        if all(p[i] != i for i in range(n)):
            return p


def particionar_em_k(rng: random.Random, itens: Sequence[T], k: int) -> list[list[T]]:
    """k grupos com tamanhos que diferem em no máximo 1, após embaralhar."""
    if k < 1:
        raise ValueError("k deve ser >= 1")
    a = fisher_yates(rng, itens)
    base, extra = divmod(len(a), k)
    grupos: list[list[T]] = []
    pos = 0
    for g in range(k):
        tam = base + (1 if g < extra else 0)
        grupos.append(a[pos:pos + tam])
        pos += tam
    return grupos


def dividir_treino_teste(
    rng: random.Random, itens: Sequence[T], fracao_teste: float
) -> tuple[list[T], list[T]]:
    if not 0.0 <= fracao_teste <= 1.0:
        raise ValueError("fração deve estar em [0, 1]")
    a = fisher_yates(rng, itens)
    n_teste = round(len(a) * fracao_teste)
    return a[n_teste:], a[:n_teste]


def dobras_cruzadas(rng: random.Random, itens: Sequence[T], k: int) -> list[tuple[list[T], list[T]]]:
    """k pares (treino, validação); cada item aparece em exatamente uma validação."""
    grupos = particionar_em_k(rng, itens, k)
    return [
        ([x for j, g in enumerate(grupos) if j != i for x in g], grupos[i])
        for i in range(k)
    ]
