"""Correção monetária por índice (variações percentuais ou números-índice)."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def fator_acumulado(variacoes_percentuais: Sequence[object]) -> Decimal:
    """Produto de (1 + v/100) para cada variação mensal em %."""
    fator = Decimal(1)
    for v in variacoes_percentuais:
        pct = _d(v)
        if pct <= -100:
            raise ValueError("variação deve ser maior que -100%")
        fator *= 1 + pct / 100
    return fator


def corrigir_por_variacoes(valor: object, variacoes_percentuais: Sequence[object]) -> Decimal:
    """Corrige `valor` pelas variações em % (ex.: IPCA mensal de cada mês)."""
    return _q(_d(valor) * fator_acumulado(variacoes_percentuais))


def corrigir_por_indices(valor: object, indice_inicial: object, indice_final: object) -> Decimal:
    """Corrige por números-índice: valor * final / inicial."""
    ini, fim = _d(indice_inicial), _d(indice_final)
    if ini <= 0 or fim <= 0:
        raise ValueError("índices devem ser positivos")
    return _q(_d(valor) * fim / ini)


def variacao_acumulada_percentual(variacoes_percentuais: Sequence[object]) -> Decimal:
    return (fator_acumulado(variacoes_percentuais) - 1) * 100
