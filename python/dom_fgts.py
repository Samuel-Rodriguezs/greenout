"""FGTS: depósito mensal, saldo com correção e multa rescisória.

Percentuais padrão (8%, 2% aprendiz, 40%) são exemplos parametrizáveis.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

CENTAVOS = Decimal("0.01")
ALIQUOTA_PADRAO = Decimal("0.08")
ALIQUOTA_APRENDIZ = Decimal("0.02")
MULTA_SEM_JUSTA_CAUSA = Decimal("0.40")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def deposito_mensal(remuneracao: object, aliquota: Decimal = ALIQUOTA_PADRAO) -> Decimal:
    rem = _d(remuneracao)
    if rem < 0:
        raise ValueError("remuneração não pode ser negativa")
    return _q(rem * aliquota)


def saldo_acumulado(depositos: Sequence[object], taxa_mensal: object = 0) -> Decimal:
    """Cada mês: saldo = saldo * (1 + taxa) + depósito."""
    t = _d(taxa_mensal)
    if t < 0:
        raise ValueError("taxa não pode ser negativa")
    saldo = Decimal(0)
    for dep in depositos:
        saldo = _q(saldo * (1 + t)) + _d(dep)
    return _q(saldo)


def multa_rescisoria(saldo: object, percentual: Decimal = MULTA_SEM_JUSTA_CAUSA) -> Decimal:
    s = _d(saldo)
    if s < 0:
        raise ValueError("saldo não pode ser negativo")
    return _q(s * percentual)
