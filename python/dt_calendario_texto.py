"""Calendário mensal em texto (semana começando no domingo), com destaque opcional de dias."""
from __future__ import annotations

import calendar
from collections.abc import Iterable

MESES = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)
CABECALHO = "Do Se Te Qu Qu Se Sa"
_LARGURA = len(CABECALHO)


def semanas_do_mes(ano: int, mes: int) -> list[list[int]]:
    """Semanas (domingo a sábado) com 0 nos dias fora do mês."""
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdayscalendar(ano, mes)


def calendario_mensal(ano: int, mes: int, destacar: Iterable[int] = ()) -> str:
    """Texto do calendário. Dias em `destacar` aparecem entre colchetes, ex.: [14]."""
    if not 1 <= mes <= 12:
        raise ValueError("mês inválido")
    marcados = set(destacar)
    titulo = f"{MESES[mes - 1]} {ano}".center(_LARGURA).rstrip()
    linhas = [titulo, CABECALHO]
    for semana in semanas_do_mes(ano, mes):
        celulas = []
        for dia in semana:
            if dia == 0:
                celulas.append("  ")
            elif dia in marcados:
                celulas.append(f"[{dia}]")
            else:
                celulas.append(f"{dia:2d}")
        linhas.append(" ".join(celulas).rstrip())
    return "\n".join(linhas)
