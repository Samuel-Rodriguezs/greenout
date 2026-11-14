"""K-means com inicialização k-means++ (determinística por seed)."""
from __future__ import annotations

import random


def _d2(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def inicializar_pp(X: list[list[float]], k: int, rng: random.Random) -> list[list[float]]:
    centros = [list(X[rng.randrange(len(X))])]
    while len(centros) < k:
        dist = [min(_d2(x, c) for c in centros) for x in X]
        total = sum(dist)
        if total == 0:
            centros.append(list(X[rng.randrange(len(X))]))
            continue
        alvo = rng.random() * total
        acum = 0.0
        for x, d in zip(X, dist):
            acum += d
            if acum >= alvo:
                centros.append(list(x))
                break
        else:
            centros.append(list(X[-1]))
    return centros


def kmeans(X: list[list[float]], k: int, seed: int = 0, max_iter: int = 100
           ) -> tuple[list[list[float]], list[int], float]:
    """Retorna (centros, rótulos, inércia)."""
    if k < 1 or k > len(X):
        raise ValueError("k deve estar entre 1 e len(X)")
    rng = random.Random(seed)
    centros = inicializar_pp(X, k, rng)
    rotulos = [-1] * len(X)
    for _ in range(max_iter):
        novos = [min(range(k), key=lambda c: _d2(x, centros[c])) for x in X]
        if novos == rotulos:
            break
        rotulos = novos
        for c in range(k):
            membros = [x for x, r in zip(X, rotulos) if r == c]
            if membros:
                centros[c] = [sum(col) / len(membros) for col in zip(*membros)]
    inercia = sum(_d2(x, centros[r]) for x, r in zip(X, rotulos))
    return centros, rotulos, inercia
