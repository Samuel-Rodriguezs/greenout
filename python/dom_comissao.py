"""Comissão escalonada. Faixas e percentuais são EXEMPLOS parametrizáveis."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Sequence

CENTAVOS = Decimal("0.01")

# (limite superior da faixa de vendas, percentual); None = sem limite.
FAIXAS_EXEMPLO: tuple[tuple[Optional[Decimal], Decimal], ...] = (
    (Decimal("10000"), Decimal("0.02")),
    (Decimal("20000"), Decimal("0.03")),
    (None, Decimal("0.05")),
)


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _validar(vendas: Decimal, faixas: Sequence[tuple[Optional[Decimal], Decimal]]) -> None:
    if vendas < 0:
        raise ValueError("vendas não pode ser negativo")
    limites = [l for l, _ in faixas if l is not None]
    if limites != sorted(set(limites)):
        raise ValueError("limites devem ser crescentes e distintos")
    if not faixas or faixas[-1][0] is not None:
        raise ValueError("a última faixa deve ser aberta (limite None)")


def comissao_marginal(vendas: object,
                      faixas: Sequence[tuple[Optional[Decimal], Decimal]] = FAIXAS_EXEMPLO
                      ) -> Decimal:
    """Cada percentual incide só sobre a parcela das vendas dentro da faixa."""
    v = Decimal(str(vendas))
    _validar(v, faixas)
    anterior = Decimal(0)
    total = Decimal(0)
    for limite, pct in faixas:
        topo = v if limite is None else min(v, limite)
        if topo > anterior:
            total += (topo - anterior) * pct
        if limite is None or v <= limite:
            break
        anterior = limite
    return _q(total)


def comissao_global(vendas: object,
                    faixas: Sequence[tuple[Optional[Decimal], Decimal]] = FAIXAS_EXEMPLO
                    ) -> Decimal:
    """O percentual da faixa em que as vendas caem incide sobre o total."""
    v = Decimal(str(vendas))
    _validar(v, faixas)
    for limite, pct in faixas:
        if limite is None or v <= limite:
            return _q(v * pct)
    raise ValueError("faixas inválidas")
