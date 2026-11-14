"""Dias úteis: verificação, vizinhança, soma e contagem, com lista de feriados injetável."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta


def _conjunto(feriados: Iterable[date] | None) -> frozenset[date]:
    return frozenset(feriados) if feriados is not None else frozenset()


def eh_dia_util(d: date, feriados: Iterable[date] | None = None) -> bool:
    """Segunda a sexta que não esteja na lista de feriados."""
    return d.weekday() < 5 and d not in _conjunto(feriados)


def proximo_dia_util(d: date, feriados: Iterable[date] | None = None) -> date:
    """Primeiro dia útil estritamente posterior a d."""
    fer = _conjunto(feriados)
    atual = d + timedelta(days=1)
    while not eh_dia_util(atual, fer):
        atual += timedelta(days=1)
    return atual


def dia_util_anterior(d: date, feriados: Iterable[date] | None = None) -> date:
    """Último dia útil estritamente anterior a d."""
    fer = _conjunto(feriados)
    atual = d - timedelta(days=1)
    while not eh_dia_util(atual, fer):
        atual -= timedelta(days=1)
    return atual


def ajustar_para_dia_util(d: date, feriados: Iterable[date] | None = None, para_tras: bool = False) -> date:
    """Se d não for útil, avança (ou recua) até o dia útil mais próximo."""
    fer = _conjunto(feriados)
    if eh_dia_util(d, fer):
        return d
    return dia_util_anterior(d, fer) if para_tras else proximo_dia_util(d, fer)


def somar_dias_uteis(d: date, n: int, feriados: Iterable[date] | None = None) -> date:
    """Soma (ou subtrai, se n < 0) n dias úteis a d."""
    fer = _conjunto(feriados)
    atual = d
    for _ in range(abs(n)):
        atual = proximo_dia_util(atual, fer) if n > 0 else dia_util_anterior(atual, fer)
    return atual


def contar_dias_uteis(inicio: date, fim: date, feriados: Iterable[date] | None = None) -> int:
    """Dias úteis em [inicio, fim). Negativo se fim < inicio (semântica de busday_count)."""
    fer = _conjunto(feriados)
    if fim < inicio:
        return -contar_dias_uteis(fim, inicio, fer)
    total = (fim - inicio).days
    semanas, resto = divmod(total, 7)
    uteis = semanas * 5
    for i in range(resto):
        if (inicio + timedelta(days=i)).weekday() < 5:
            uteis += 1
    for h in fer:
        if inicio <= h < fim and h.weekday() < 5:
            uteis -= 1
    return uteis
