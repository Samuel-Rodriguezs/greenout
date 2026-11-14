"""Multa e juros de mora por atraso.

Multa (2%) e juros (1% ao mês, pro rata dia sobre 30 dias) são exemplos
parametrizáveis.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")
MULTA_PADRAO = Decimal("0.02")
JUROS_MENSAL_PADRAO = Decimal("0.01")


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Atraso:
    dias: int
    multa: Decimal
    juros: Decimal
    total: Decimal


def dias_de_atraso(vencimento: date, pagamento: date) -> int:
    """Dias corridos após o vencimento (0 se pago em dia ou antes)."""
    return max((pagamento - vencimento).days, 0)


def calcular_mora(valor: object, vencimento: date, pagamento: date,
                  multa: Decimal = MULTA_PADRAO,
                  juros_mensal: Decimal = JUROS_MENSAL_PADRAO,
                  composto: bool = False) -> Atraso:
    """Multa fixa sobre o valor + juros pro rata (simples por padrão)."""
    v = Decimal(str(valor))
    if v < 0:
        raise ValueError("valor não pode ser negativo")
    dias = dias_de_atraso(vencimento, pagamento)
    if dias == 0:
        return Atraso(0, Decimal("0.00"), Decimal("0.00"), _q(v))
    valor_multa = _q(v * multa)
    if composto:
        juros = _q(v * ((1 + juros_mensal) ** (Decimal(dias) / 30) - 1))
    else:
        juros = _q(v * juros_mensal / 30 * dias)
    return Atraso(dias, valor_multa, juros, _q(v) + valor_multa + juros)
