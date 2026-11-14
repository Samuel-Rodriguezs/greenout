"""Volatilidade histórica de retornos (amostral), anualizada e em janela."""
from __future__ import annotations

import math


def desvio_amostral(valores: list[float]) -> float:
    if len(valores) < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    media = sum(valores) / len(valores)
    return math.sqrt(sum((v - media) ** 2 for v in valores) / (len(valores) - 1))


def volatilidade(retornos: list[float], periodos_ano: int = 252) -> float:
    """Desvio-padrão amostral dos retornos multiplicado por raiz(periodos_ano)."""
    return desvio_amostral(retornos) * math.sqrt(periodos_ano)


def volatilidade_movel(
    retornos: list[float], janela: int, periodos_ano: int = 252
) -> list[float | None]:
    if janela < 2:
        raise ValueError("janela deve ser >= 2")
    saida: list[float | None] = [None] * len(retornos)
    for i in range(janela - 1, len(retornos)):
        saida[i] = volatilidade(retornos[i - janela + 1 : i + 1], periodos_ano)
    return saida
