"""Tabela Price (parcelas fixas). Taxa como fração por período."""
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


def parcela_price(principal: object, taxa: object, n: int) -> Decimal:
    """PMT = PV * i / (1 - (1+i)^-n); com taxa zero, PV / n."""
    pv, i = _d(principal), _d(taxa)
    if n <= 0:
        raise ValueError("número de parcelas deve ser positivo")
    if pv < 0 or i < 0:
        raise ValueError("principal e taxa não podem ser negativos")
    if i == 0:
        return _q(pv / n)
    return _q(pv * i / (1 - (1 + i) ** -n))


def tabela_price(principal: object, taxa: object, n: int) -> list[Linha]:
    """Gera a tabela; a última parcela absorve a diferença de arredondamento."""
    pv, i = _q(_d(principal)), _d(taxa)
    pmt = parcela_price(pv, i, n)
    saldo = pv
    linhas: list[Linha] = []
    for k in range(1, n + 1):
        juros = _q(saldo * i)
        if k == n:
            amort = saldo
            parcela = amort + juros
        else:
            amort = pmt - juros
            parcela = pmt
        saldo = saldo - amort
        linhas.append(Linha(k, parcela, juros, amort, saldo))
    return linhas
