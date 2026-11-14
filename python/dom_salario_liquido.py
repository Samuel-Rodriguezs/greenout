"""Salário líquido = bruto - INSS - IRRF - outros descontos.

Usa as tabelas de EXEMPLO de dom_inss e dom_irrf (parametrizáveis).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from dom_inss import FAIXAS_EXEMPLO as INSS_EXEMPLO, calcular_inss
from dom_irrf import FAIXAS_EXEMPLO as IRRF_EXEMPLO, calcular_irrf

CENTAVOS = Decimal("0.01")


@dataclass(frozen=True)
class Holerite:
    bruto: Decimal
    inss: Decimal
    irrf: Decimal
    outros: Decimal
    liquido: Decimal


def calcular_liquido(bruto: object, dependentes: int = 0, outros_descontos: object = 0,
                     faixas_inss=INSS_EXEMPLO, faixas_irrf=IRRF_EXEMPLO) -> Holerite:
    b = Decimal(str(bruto)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    outros = Decimal(str(outros_descontos)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    if b < 0 or outros < 0:
        raise ValueError("valores não podem ser negativos")
    inss = calcular_inss(b, faixas_inss)
    irrf = calcular_irrf(b, inss, dependentes, faixas_irrf)
    liquido = b - inss - irrf - outros
    return Holerite(b, inss, irrf, outros, liquido)
