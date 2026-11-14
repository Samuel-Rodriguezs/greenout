"""Contagem de prazos em dias corridos ou úteis (estilo processual: exclui o dia do começo)."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

from dt_dias_uteis import ajustar_para_dia_util, contar_dias_uteis, somar_dias_uteis

TIPOS = ("corridos", "uteis")


def _validar_tipo(tipo: str) -> None:
    if tipo not in TIPOS:
        raise ValueError(f"tipo de prazo inválido: {tipo!r} (use 'corridos' ou 'uteis')")


def calcular_vencimento(
    inicio: date,
    dias: int,
    tipo: str = "corridos",
    feriados: Iterable[date] | None = None,
    prorrogar: bool = True,
) -> date:
    """Vencimento de um prazo que começa a contar no dia seguinte a `inicio`.

    - dias úteis: pula fins de semana e feriados;
    - dias corridos: soma direta e, se `prorrogar`, o vencimento que cair em dia
      não útil passa para o primeiro dia útil seguinte.
    """
    _validar_tipo(tipo)
    if dias < 0:
        raise ValueError("o prazo não pode ser negativo")
    fer = frozenset(feriados) if feriados is not None else frozenset()
    if tipo == "uteis":
        return somar_dias_uteis(inicio, dias, fer)
    venc = inicio + timedelta(days=dias)
    return ajustar_para_dia_util(venc, fer) if prorrogar else venc


def dias_restantes(
    vencimento: date,
    hoje: date,
    tipo: str = "corridos",
    feriados: Iterable[date] | None = None,
) -> int:
    """Dias que faltam de `hoje` (exclusive) até o vencimento (inclusive); negativo se vencido."""
    _validar_tipo(tipo)
    if tipo == "corridos":
        return (vencimento - hoje).days
    um_dia = timedelta(days=1)
    return contar_dias_uteis(hoje + um_dia, vencimento + um_dia, feriados)


def esta_vencido(
    vencimento: date,
    hoje: date,
) -> bool:
    return hoje > vencimento
