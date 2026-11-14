"""Payback simples e descontado (em períodos, com fração linear)."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional, Sequence


def payback(fluxos: Sequence[object], taxa: object = 0) -> Optional[Decimal]:
    """Períodos até recuperar o investimento (fluxo 0 negativo).

    Com `taxa` > 0 desconta cada fluxo (payback descontado). Retorna None se
    o investimento nunca é recuperado. A fração dentro do período é linear.
    """
    i = Decimal(str(taxa))
    if i < 0:
        raise ValueError("taxa não pode ser negativa")
    if not fluxos:
        raise ValueError("fluxos vazios")
    acumulado = Decimal(0)
    for t, fluxo in enumerate(fluxos):
        valor = Decimal(str(fluxo)) / (1 + i) ** t
        anterior = acumulado
        acumulado += valor
        if acumulado >= 0:
            if t == 0:
                return Decimal(0)
            return Decimal(t - 1) + (-anterior) / valor
    return None
