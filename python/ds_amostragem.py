"""Amostragem e bootstrap reprodutíveis (com seed)."""
from __future__ import annotations

import random
from typing import Any, Callable, Sequence


def amostra_simples(dados: Sequence[Any], k: int, seed: int | None = None) -> list[Any]:
    """Amostra sem reposição."""
    if not 0 <= k <= len(dados):
        raise ValueError("k fora do intervalo [0, len(dados)]")
    return random.Random(seed).sample(list(dados), k)


def amostra_com_reposicao(dados: Sequence[Any], k: int, seed: int | None = None) -> list[Any]:
    if not dados:
        raise ValueError("dados vazios")
    if k < 0:
        raise ValueError("k deve ser não negativo")
    return random.Random(seed).choices(list(dados), k=k)


def amostra_estratificada(
    registros: Sequence[dict[str, Any]], chave: str, fracao: float, seed: int | None = None
) -> list[dict[str, Any]]:
    """Sorteia round(fracao * tamanho) registros de cada estrato (mínimo 1)."""
    if not 0 < fracao <= 1:
        raise ValueError("fração deve estar em (0, 1]")
    rng = random.Random(seed)
    estratos: dict[Any, list[dict[str, Any]]] = {}
    for r in registros:
        estratos.setdefault(r[chave], []).append(r)
    saida: list[dict[str, Any]] = []
    for membros in estratos.values():
        saida.extend(rng.sample(membros, max(1, round(fracao * len(membros)))))
    return saida


def bootstrap(
    dados: Sequence[float],
    estatistica: Callable[[Sequence[float]], float],
    n_reamostras: int = 1000,
    seed: int | None = None,
) -> list[float]:
    """Distribuição bootstrap da estatística."""
    if not dados:
        raise ValueError("dados vazios")
    if n_reamostras <= 0:
        raise ValueError("n_reamostras deve ser positivo")
    rng = random.Random(seed)
    n = len(dados)
    pool = list(dados)
    return [estatistica(rng.choices(pool, k=n)) for _ in range(n_reamostras)]


def _quantil(ordenado: list[float], p: float) -> float:
    pos = p * (len(ordenado) - 1)
    i = int(pos)
    if i + 1 >= len(ordenado):
        return ordenado[-1]
    return ordenado[i] + (pos - i) * (ordenado[i + 1] - ordenado[i])


def ic_bootstrap(
    dados: Sequence[float],
    estatistica: Callable[[Sequence[float]], float],
    confianca: float = 0.95,
    n_reamostras: int = 1000,
    seed: int | None = None,
) -> tuple[float, float]:
    """Intervalo percentil do bootstrap."""
    if not 0 < confianca < 1:
        raise ValueError("confiança deve estar em (0, 1)")
    dist = sorted(bootstrap(dados, estatistica, n_reamostras, seed))
    alfa = (1 - confianca) / 2
    return _quantil(dist, alfa), _quantil(dist, 1 - alfa)
