"""Beta e alfa de Jensen de um ativo contra um benchmark."""
from __future__ import annotations


def _media(v: list[float]) -> float:
    return sum(v) / len(v)


def covariancia(a: list[float], b: list[float]) -> float:
    """Covariância amostral."""
    if len(a) != len(b):
        raise ValueError("séries com tamanhos diferentes")
    if len(a) < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    ma, mb = _media(a), _media(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (len(a) - 1)


def beta(ativo: list[float], benchmark: list[float]) -> float:
    var_b = covariancia(benchmark, benchmark)
    if var_b == 0:
        raise ValueError("benchmark sem variância")
    return covariancia(ativo, benchmark) / var_b


def alfa_jensen(
    ativo: list[float], benchmark: list[float], taxa_livre: float = 0.0
) -> float:
    """alfa = E[Ra] - rf - beta * (E[Rb] - rf), por período."""
    b = beta(ativo, benchmark)
    return _media(ativo) - taxa_livre - b * (_media(benchmark) - taxa_livre)
