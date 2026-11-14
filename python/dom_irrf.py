"""IRRF mensal (tabela progressiva com parcela a deduzir).

ATENÇÃO: faixas, alíquotas e dedução por dependente são apenas EXEMPLO
didático; informe os valores vigentes pelos parâmetros.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Sequence

CENTAVOS = Decimal("0.01")

# (limite superior da base, alíquota, parcela a deduzir); None = sem limite.
FAIXAS_EXEMPLO: tuple[tuple[Optional[Decimal], Decimal, Decimal], ...] = (
    (Decimal("2259.20"), Decimal("0"), Decimal("0")),
    (Decimal("2826.65"), Decimal("0.075"), Decimal("169.44")),
    (Decimal("3751.05"), Decimal("0.15"), Decimal("381.44")),
    (Decimal("4664.68"), Decimal("0.225"), Decimal("662.77")),
    (None, Decimal("0.275"), Decimal("896.00")),
)
DEDUCAO_DEPENDENTE_EXEMPLO = Decimal("189.59")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def irrf_sobre_base(base: object,
                    faixas: Sequence[tuple[Optional[Decimal], Decimal, Decimal]] = FAIXAS_EXEMPLO
                    ) -> Decimal:
    """Imposto = base * alíquota - parcela a deduzir (nunca negativo)."""
    b = _d(base)
    if b <= 0:
        return Decimal("0.00")
    for limite, aliquota, deducao in faixas:
        if limite is None or b <= limite:
            imposto = b * aliquota - deducao
            return max(imposto, Decimal(0)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    raise ValueError("tabela sem faixa final aberta")


def calcular_irrf(bruto: object, inss: object = 0, dependentes: int = 0,
                  faixas: Sequence[tuple[Optional[Decimal], Decimal, Decimal]] = FAIXAS_EXEMPLO,
                  deducao_dependente: Decimal = DEDUCAO_DEPENDENTE_EXEMPLO) -> Decimal:
    """Base = bruto - INSS - dependentes * dedução; depois aplica a tabela."""
    if dependentes < 0:
        raise ValueError("dependentes não pode ser negativo")
    if _d(bruto) < 0 or _d(inss) < 0:
        raise ValueError("valores não podem ser negativos")
    base = _d(bruto) - _d(inss) - dependentes * deducao_dependente
    return irrf_sobre_base(base, faixas)
