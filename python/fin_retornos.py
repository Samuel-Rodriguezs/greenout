"""Retornos simples, logarítmicos, acumulado e anualizado."""
from __future__ import annotations

import math


def _validar(precos: list[float]) -> None:
    if any(p <= 0 for p in precos):
        raise ValueError("preços devem ser positivos")


def retornos_simples(precos: list[float]) -> list[float]:
    _validar(precos)
    return [precos[i] / precos[i - 1] - 1 for i in range(1, len(precos))]


def retornos_log(precos: list[float]) -> list[float]:
    _validar(precos)
    return [math.log(precos[i] / precos[i - 1]) for i in range(1, len(precos))]


def retorno_acumulado(retornos: list[float]) -> float:
    """Produto de (1 + r) menos 1."""
    fator = 1.0
    for r in retornos:
        fator *= 1 + r
    return fator - 1


def retorno_anualizado(retorno_total: float, dias: int, base: int = 252) -> float:
    """Converte retorno total em `dias` dias úteis para taxa anual."""
    if dias <= 0:
        raise ValueError("dias deve ser positivo")
    if retorno_total <= -1:
        raise ValueError("retorno total deve ser maior que -100%")
    return (1 + retorno_total) ** (base / dias) - 1
