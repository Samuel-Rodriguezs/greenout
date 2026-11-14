"""Rateio de despesas proporcional a pesos, sem perder centavos (maiores restos)."""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Sequence


def ratear(total: object, pesos: Sequence[object]) -> list[Decimal]:
    """Divide `total` em partes proporcionais a `pesos`; a soma é exatamente `total`.

    Cada parte é truncada em centavos e os centavos restantes vão para os
    maiores restos (empate: menor índice).
    """
    if not pesos:
        raise ValueError("pesos vazios")
    fpesos = [Fraction(str(p)) for p in pesos]
    if any(p < 0 for p in fpesos):
        raise ValueError("pesos não podem ser negativos")
    soma = sum(fpesos)
    if soma == 0:
        raise ValueError("soma dos pesos deve ser positiva")
    ftotal = Fraction(str(total))
    centavos_total = ftotal * 100
    if centavos_total.denominator != 1 or centavos_total < 0:
        raise ValueError("total deve ser não negativo e ter no máximo 2 casas decimais")
    alvo = int(centavos_total)
    exatos = [alvo * p / soma for p in fpesos]
    base = [int(e) for e in exatos]  # e >= 0: int() trunca
    sobra = alvo - sum(base)
    ordem = sorted(range(len(pesos)), key=lambda k: (-(exatos[k] - base[k]), k))
    for k in ordem[:sobra]:
        base[k] += 1
    return [Decimal(c) / 100 for c in base]


def ratear_igualmente(total: object, partes: int) -> list[Decimal]:
    if partes <= 0:
        raise ValueError("partes deve ser positivo")
    return ratear(total, [1] * partes)
