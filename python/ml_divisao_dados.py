"""Train/test split e k-fold com embaralhamento determinístico por seed."""
from __future__ import annotations

import random
from typing import Iterator


def train_test_split(X: list, y: list, proporcao_teste: float = 0.25, seed: int = 0,
                     embaralhar: bool = True) -> tuple[list, list, list, list]:
    if len(X) != len(y):
        raise ValueError("X e y devem ter o mesmo tamanho")
    if not 0 < proporcao_teste < 1:
        raise ValueError("proporcao_teste deve estar em (0, 1)")
    n = len(X)
    idx = list(range(n))
    if embaralhar:
        random.Random(seed).shuffle(idx)
    n_teste = max(1, round(n * proporcao_teste))
    if n_teste >= n:
        raise ValueError("dados insuficientes para dividir")
    teste, treino = idx[:n_teste], idx[n_teste:]
    return ([X[i] for i in treino], [X[i] for i in teste],
            [y[i] for i in treino], [y[i] for i in teste])


def k_fold(n: int, k: int = 5, seed: int = 0, embaralhar: bool = True
           ) -> Iterator[tuple[list[int], list[int]]]:
    """Gera (índices_treino, índices_validação) para cada dobra."""
    if not 2 <= k <= n:
        raise ValueError("k deve estar entre 2 e n")
    idx = list(range(n))
    if embaralhar:
        random.Random(seed).shuffle(idx)
    base, resto = divmod(n, k)
    inicio = 0
    for i in range(k):
        tam = base + (1 if i < resto else 0)
        val = idx[inicio:inicio + tam]
        treino = idx[:inicio] + idx[inicio + tam:]
        yield treino, val
        inicio += tam


def k_fold_estratificado(y: list, k: int = 5, seed: int = 0) -> Iterator[tuple[list[int], list[int]]]:
    """Dobras que preservam (aprox.) a proporção de classes."""
    if not 2 <= k <= len(y):
        raise ValueError("k deve estar entre 2 e len(y)")
    rng = random.Random(seed)
    dobras: list[list[int]] = [[] for _ in range(k)]
    por_classe: dict = {}
    for i, r in enumerate(y):
        por_classe.setdefault(r, []).append(i)
    pos = 0
    for classe in sorted(por_classe, key=str):
        itens = por_classe[classe]
        rng.shuffle(itens)
        for i in itens:
            dobras[pos % k].append(i)
            pos += 1
    for i in range(k):
        treino = [j for d in range(k) if d != i for j in dobras[d]]
        yield treino, sorted(dobras[i])
