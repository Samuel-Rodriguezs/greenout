"""Índices de Sharpe e Sortino a partir de retornos periódicos."""
from __future__ import annotations

import math


def _media(v: list[float]) -> float:
    return sum(v) / len(v)


def sharpe(
    retornos: list[float], taxa_livre: float = 0.0, periodos_ano: int = 252
) -> float:
    """Média do excesso de retorno / desvio amostral, anualizado por raiz(T)."""
    if len(retornos) < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    excessos = [r - taxa_livre for r in retornos]
    m = _media(excessos)
    dp = math.sqrt(sum((x - m) ** 2 for x in excessos) / (len(excessos) - 1))
    if dp == 0:
        raise ValueError("desvio-padrão nulo")
    return m / dp * math.sqrt(periodos_ano)


def sortino(
    retornos: list[float], alvo: float = 0.0, periodos_ano: int = 252
) -> float:
    """Excesso médio sobre o alvo / desvio de downside, anualizado."""
    if not retornos:
        raise ValueError("série vazia")
    downside = math.sqrt(sum(min(r - alvo, 0.0) ** 2 for r in retornos) / len(retornos))
    if downside == 0:
        raise ValueError("sem retornos abaixo do alvo")
    return (_media(retornos) - alvo) / downside * math.sqrt(periodos_ano)
