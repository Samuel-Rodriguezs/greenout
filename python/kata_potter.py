"""Potter Kata: melhor preço para uma cesta de livros com descontos por conjunto."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache

PRECO_UNITARIO = 800  # centavos
DESCONTOS = {1: 0, 2: 5, 3: 10, 4: 20, 5: 25}  # percentual por tamanho de conjunto


def _preco_conjunto(tamanho: int) -> int:
    return tamanho * PRECO_UNITARIO * (100 - DESCONTOS[tamanho]) // 100


@lru_cache(maxsize=None)
def _melhor(contagens: tuple[int, ...]) -> int:
    contagens = tuple(sorted((c for c in contagens if c > 0), reverse=True))
    if not contagens:
        return 0
    melhor = None
    for k in range(1, len(contagens) + 1):
        restante = tuple(c - 1 if i < k else c for i, c in enumerate(contagens))
        custo = _preco_conjunto(k) + _melhor(restante)
        if melhor is None or custo < melhor:
            melhor = custo
    return melhor


def preco(livros: list[int]) -> int:
    """Preço em centavos da cesta; cada livro é um inteiro de 1 a 5 (o volume)."""
    if any(l not in (1, 2, 3, 4, 5) for l in livros):
        raise ValueError("volumes válidos: 1 a 5")
    return _melhor(tuple(Counter(livros).values()))
