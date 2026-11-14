"""Valor Presente Líquido (VPL). O fluxo 0 é o investimento inicial (sem desconto)."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def vpl_exato(taxa: object, fluxos: Sequence[object]) -> Decimal:
    """VPL sem arredondamento: soma de FC_t / (1+i)^t, t = 0, 1, ..."""
    i = _d(taxa)
    if i <= -1:
        raise ValueError("taxa deve ser maior que -100%")
    if not fluxos:
        raise ValueError("fluxos vazios")
    return sum((_d(fc) / (1 + i) ** t for t, fc in enumerate(fluxos)), Decimal(0))


def vpl(taxa: object, fluxos: Sequence[object]) -> Decimal:
    return vpl_exato(taxa, fluxos).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def vale_a_pena(taxa: object, fluxos: Sequence[object]) -> bool:
    """Projeto aceitável quando VPL > 0."""
    return vpl_exato(taxa, fluxos) > 0
