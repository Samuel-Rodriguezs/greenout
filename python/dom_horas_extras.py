"""Horas extras e adicional noturno.

Percentuais (50%, 100%, 20%) e jornada mensal (220h) são valores de exemplo
parametrizáveis.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")
JORNADA_MENSAL = Decimal(220)
ADICIONAL_50 = Decimal("0.50")
ADICIONAL_100 = Decimal("1.00")
ADICIONAL_NOTURNO = Decimal("0.20")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def valor_hora(salario: object, jornada_mensal: Decimal = JORNADA_MENSAL) -> Decimal:
    sal = _d(salario)
    if sal < 0 or jornada_mensal <= 0:
        raise ValueError("salário e jornada devem ser positivos")
    return sal / jornada_mensal


def valor_horas_extras(salario: object, horas: object, adicional: Decimal = ADICIONAL_50,
                       jornada_mensal: Decimal = JORNADA_MENSAL) -> Decimal:
    """Total pago por `horas` extras: horas * valor_hora * (1 + adicional)."""
    h = _d(horas)
    if h < 0 or adicional < 0:
        raise ValueError("horas e adicional não podem ser negativos")
    return _q(h * valor_hora(salario, jornada_mensal) * (1 + adicional))


def adicional_noturno(salario: object, horas_noturnas: object,
                      percentual: Decimal = ADICIONAL_NOTURNO,
                      jornada_mensal: Decimal = JORNADA_MENSAL) -> Decimal:
    """Apenas o adicional (20%) sobre as horas noturnas trabalhadas."""
    h = _d(horas_noturnas)
    if h < 0:
        raise ValueError("horas não pode ser negativo")
    return _q(h * valor_hora(salario, jornada_mensal) * percentual)


def horas_noturnas_computadas(horas_relogio: object) -> Decimal:
    """Hora noturna reduzida: 52min30s equivale a 1 hora (60 / 52,5)."""
    h = _d(horas_relogio)
    if h < 0:
        raise ValueError("horas não pode ser negativo")
    return h * 60 / Decimal("52.5")
