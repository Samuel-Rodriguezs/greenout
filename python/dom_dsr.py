"""Descanso Semanal Remunerado (DSR) sobre verbas variáveis (horas extras, comissões)."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

CENTAVOS = Decimal("0.01")


def dias_do_mes(ano: int, mes: int, feriados: Iterable[date] = ()) -> tuple[int, int]:
    """Retorna (dias úteis, dias de descanso) do mês.

    Descanso = domingos + feriados que não caem em domingo; úteis = demais dias.
    """
    total = calendar.monthrange(ano, mes)[1]
    feriados_mes = {f for f in feriados if f.year == ano and f.month == mes}
    descanso = 0
    for dia in range(1, total + 1):
        d = date(ano, mes, dia)
        if d.weekday() == 6 or d in feriados_mes:
            descanso += 1
    return total - descanso, descanso


def calcular_dsr(valor_variavel: object, ano: int, mes: int,
                 feriados: Iterable[date] = ()) -> Decimal:
    """DSR = variável / dias úteis * dias de descanso."""
    v = Decimal(str(valor_variavel))
    if v < 0:
        raise ValueError("valor não pode ser negativo")
    uteis, descanso = dias_do_mes(ano, mes, feriados)
    return (v / uteis * descanso).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
