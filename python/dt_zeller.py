"""Dia da semana pela congruência de Zeller (calendário gregoriano)."""
from __future__ import annotations

from datetime import date

# Zeller: 0 = sábado, 1 = domingo, ..., 6 = sexta-feira.
_NOMES = (
    "sábado", "domingo", "segunda-feira", "terça-feira",
    "quarta-feira", "quinta-feira", "sexta-feira",
)


def zeller(ano: int, mes: int, dia: int) -> int:
    """Índice de Zeller (0 = sábado). Valida a data."""
    date(ano, mes, dia)
    if mes < 3:  # janeiro e fevereiro contam como meses 13 e 14 do ano anterior
        mes += 12
        ano -= 1
    k = ano % 100
    j = ano // 100
    return (dia + (13 * (mes + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7


def dia_da_semana(ano: int, mes: int, dia: int) -> str:
    """Nome do dia da semana em português."""
    return _NOMES[zeller(ano, mes, dia)]


def para_weekday(ano: int, mes: int, dia: int) -> int:
    """Converte o índice de Zeller para a convenção do Python (0 = segunda)."""
    return (zeller(ano, mes, dia) + 5) % 7
