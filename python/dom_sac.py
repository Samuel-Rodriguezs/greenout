"""Sistema de Amortização Constante (SAC)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Linha:
    numero: int
    parcela: Decimal
    juros: Decimal
    amortizacao: Decimal
    saldo: Decimal


def tabela_sac(principal: object, taxa: object, n: int) -> list[Linha]:
    """Amortização fixa PV/n; juros sobre o saldo devedor. A última linha zera o saldo."""
    pv, i = _q(_d(principal)), _d(taxa)
    if n <= 0:
        raise ValueError("número de parcelas deve ser positivo")
    if pv < 0 or i < 0:
        raise ValueError("principal e taxa não podem ser negativos")
    base = _q(pv / n)
    saldo = pv
    linhas: list[Linha] = []
    for k in range(1, n + 1):
        juros = _q(saldo * i)
        amort = saldo if k == n else base
        saldo -= amort
        linhas.append(Linha(k, amort + juros, juros, amort, saldo))
    return linhas


def total_juros(linhas: list[Linha]) -> Decimal:
    return sum((l.juros for l in linhas), Decimal("0.00"))
