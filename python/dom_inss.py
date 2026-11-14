"""INSS do empregado com alíquotas progressivas (por faixa).

ATENÇÃO: as faixas abaixo são apenas EXEMPLO didático e mudam todo ano.
Informe a tabela vigente pelo parâmetro `faixas`.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

CENTAVOS = Decimal("0.01")

# (limite superior da faixa, alíquota). O último limite funciona como teto.
FAIXAS_EXEMPLO: tuple[tuple[Decimal, Decimal], ...] = (
    (Decimal("1412.00"), Decimal("0.075")),
    (Decimal("2666.68"), Decimal("0.09")),
    (Decimal("4000.03"), Decimal("0.12")),
    (Decimal("7786.02"), Decimal("0.14")),
)


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def calcular_inss(salario: object,
                  faixas: Sequence[tuple[Decimal, Decimal]] = FAIXAS_EXEMPLO) -> Decimal:
    """Soma, faixa a faixa, a alíquota aplicada à parcela do salário em cada faixa."""
    sal = _d(salario)
    if sal < 0:
        raise ValueError("salário não pode ser negativo")
    anterior = Decimal(0)
    total = Decimal(0)
    for limite, aliquota in faixas:
        if limite <= anterior:
            raise ValueError("limites das faixas devem ser crescentes")
        if sal <= anterior:
            break
        total += (min(sal, limite) - anterior) * aliquota
        anterior = limite
    return total.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def aliquota_efetiva(salario: object,
                     faixas: Sequence[tuple[Decimal, Decimal]] = FAIXAS_EXEMPLO) -> Decimal:
    sal = _d(salario)
    if sal <= 0:
        return Decimal(0)
    return calcular_inss(sal, faixas) / sal
