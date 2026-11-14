"""Dias úteis com feriados nacionais fixos e móveis (Carnaval, Sexta-feira Santa, Corpus Christi)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable


def pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo anônimo gregoriano)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def feriados_nacionais(ano: int, incluir_moveis: bool = True) -> set[date]:
    """Feriados nacionais. Consciência Negra (20/11) vale a partir de 2024."""
    fixos = {(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25)}
    if ano >= 2024:
        fixos.add((11, 20))
    feriados = {date(ano, m, d) for m, d in fixos}
    if incluir_moveis:
        p = pascoa(ano)
        feriados |= {p - timedelta(days=47), p - timedelta(days=2), p + timedelta(days=60)}
    return feriados


def eh_dia_util(data: date, feriados: Iterable[date] | None = None) -> bool:
    fer = set(feriados) if feriados is not None else feriados_nacionais(data.year)
    return data.weekday() < 5 and data not in fer


def _feriados_periodo(inicio: date, fim: date) -> set[date]:
    fer: set[date] = set()
    for ano in range(inicio.year, fim.year + 1):
        fer |= feriados_nacionais(ano)
    return fer


def contar_dias_uteis(inicio: date, fim: date, feriados: Iterable[date] | None = None) -> int:
    """Dias úteis em [inicio, fim], ambos inclusivos."""
    if fim < inicio:
        raise ValueError("data final anterior à inicial")
    fer = set(feriados) if feriados is not None else _feriados_periodo(inicio, fim)
    total = 0
    atual = inicio
    while atual <= fim:
        if eh_dia_util(atual, fer):
            total += 1
        atual += timedelta(days=1)
    return total


def somar_dias_uteis(data: date, n: int, feriados: Iterable[date] | None = None) -> date:
    """Avança (n > 0) ou recua (n < 0) `n` dias úteis a partir de `data`."""
    passo = 1 if n >= 0 else -1
    restante = abs(n)
    fer = set(feriados) if feriados is not None else None
    atual = data
    while restante:
        atual += timedelta(days=passo)
        if fer is None:
            util = eh_dia_util(atual, feriados_nacionais(atual.year))
        else:
            util = eh_dia_util(atual, fer)
        if util:
            restante -= 1
    return atual
