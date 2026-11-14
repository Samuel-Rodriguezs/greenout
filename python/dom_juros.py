"""Juros simples e compostos (valores monetários em Decimal).

Taxas são frações decimais: 1% = Decimal("0.01").
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _validar(capital: Decimal, periodos: int) -> None:
    if capital < 0:
        raise ValueError("capital não pode ser negativo")
    if periodos < 0:
        raise ValueError("períodos não pode ser negativo")


def juros_simples(capital: object, taxa: object, periodos: int) -> Decimal:
    """Juros J = C * i * n."""
    c, i = _d(capital), _d(taxa)
    _validar(c, periodos)
    return _q(c * i * periodos)


def montante_simples(capital: object, taxa: object, periodos: int) -> Decimal:
    return _q(_d(capital)) + juros_simples(capital, taxa, periodos)


def montante_composto(capital: object, taxa: object, periodos: int) -> Decimal:
    """Montante M = C * (1 + i)^n."""
    c, i = _d(capital), _d(taxa)
    _validar(c, periodos)
    return _q(c * (1 + i) ** periodos)


def juros_compostos(capital: object, taxa: object, periodos: int) -> Decimal:
    return montante_composto(capital, taxa, periodos) - _q(_d(capital))


def taxa_equivalente(taxa: object, de_periodos: int, para_periodos: int) -> Decimal:
    """Converte taxa de um período para outro (ex.: mensal -> anual: 1 -> 12).

    `de_periodos` e `para_periodos` indicam quantas unidades-base cada
    período contém; a taxa equivalente é (1+i)^(para/de) - 1.
    """
    if de_periodos <= 0 or para_periodos <= 0:
        raise ValueError("períodos devem ser positivos")
    i = _d(taxa)
    return (1 + i) ** (Decimal(para_periodos) / Decimal(de_periodos)) - 1
