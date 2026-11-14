"""Drawdown de uma série de preços ou de patrimônio."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrawdownMaximo:
    valor: float  # negativo ou zero (ex.: -0.25 = queda de 25%)
    indice_pico: int
    indice_vale: int
    indice_recuperacao: int | None  # primeiro índice que volta ao pico


def serie_drawdown(valores: list[float]) -> list[float]:
    """Queda percentual em relação ao máximo acumulado em cada ponto."""
    if any(v <= 0 for v in valores):
        raise ValueError("valores devem ser positivos")
    pico = float("-inf")
    saida: list[float] = []
    for v in valores:
        pico = max(pico, v)
        saida.append(v / pico - 1)
    return saida


def drawdown_maximo(valores: list[float]) -> DrawdownMaximo:
    if not valores:
        raise ValueError("série vazia")
    dds = serie_drawdown(valores)
    vale = min(range(len(dds)), key=lambda i: dds[i])
    pico = max(range(vale + 1), key=lambda i: (valores[i], -i))
    recuperacao = next(
        (i for i in range(vale + 1, len(valores)) if valores[i] >= valores[pico]),
        None,
    )
    return DrawdownMaximo(dds[vale], pico, vale, recuperacao)
