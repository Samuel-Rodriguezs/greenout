"""Número da semana ISO-8601 calculado manualmente (regra da quinta-feira)."""
from __future__ import annotations

from datetime import date, timedelta


def semana_iso(d: date) -> tuple[int, int, int]:
    """Retorna (ano ISO, semana ISO, dia da semana ISO 1=segunda..7=domingo)."""
    dia_semana = d.weekday() + 1
    quinta = d + timedelta(days=4 - dia_semana)  # a quinta-feira da mesma semana define o ano ISO
    inicio_ano = date(quinta.year, 1, 1)
    semana = (quinta - inicio_ano).days // 7 + 1
    return quinta.year, semana, dia_semana


def semanas_no_ano_iso(ano: int) -> int:
    """52 ou 53: o dia 28 de dezembro sempre está na última semana ISO do ano."""
    return semana_iso(date(ano, 12, 28))[1]


def segunda_da_semana_iso(ano: int, semana: int) -> date:
    """Segunda-feira da semana ISO indicada."""
    if not 1 <= semana <= semanas_no_ano_iso(ano):
        raise ValueError(f"semana {semana} não existe no ano ISO {ano}")
    quatro_jan = date(ano, 1, 4)  # sempre na semana 1
    segunda_semana_1 = quatro_jan - timedelta(days=quatro_jan.weekday())
    return segunda_semana_1 + timedelta(weeks=semana - 1)


def formatar_semana_iso(d: date) -> str:
    ano, semana, dia = semana_iso(d)
    return f"{ano}-W{semana:02d}-{dia}"
