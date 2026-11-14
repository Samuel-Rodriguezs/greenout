"""Prazos processuais em dias úteis, com suspensões injetáveis e alertas por proximidade."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

from dt_dias_uteis import eh_dia_util, proximo_dia_util


class Alerta(Enum):
    VENCIDO = "vencido"
    HOJE = "hoje"
    URGENTE = "urgente"
    ATENCAO = "atencao"
    NORMAL = "normal"


@dataclass(frozen=True)
class Suspensao:
    inicio: date
    fim: date  # inclusive
    motivo: str = ""

    def __post_init__(self) -> None:
        if self.fim < self.inicio:
            raise ValueError("fim anterior ao início da suspensão")

    def contem(self, d: date) -> bool:
        return self.inicio <= d <= self.fim


def recesso_forense(ano: int) -> Suspensao:
    """Suspensão de 20/12 a 20/01 (art. 220 do CPC), iniciada em 20/12 de `ano`."""
    return Suspensao(date(ano, 12, 20), date(ano + 1, 1, 20), "recesso forense")


def _conta(d: date, feriados: frozenset[date], suspensoes: tuple[Suspensao, ...]) -> bool:
    return eh_dia_util(d, feriados) and not any(s.contem(d) for s in suspensoes)


def calcular_vencimento(
    intimacao: date,
    dias_uteis: int,
    feriados: Iterable[date] = (),
    suspensoes: Iterable[Suspensao] = (),
) -> date:
    """Exclui o dia da intimação; conta só dias úteis fora das suspensões; o último dia é útil."""
    if dias_uteis < 1:
        raise ValueError("prazo deve ser de ao menos 1 dia útil")
    fer = frozenset(feriados)
    susp = tuple(suspensoes)
    atual, restante = intimacao, dias_uteis
    while restante:
        atual += timedelta(days=1)
        if _conta(atual, fer, susp):
            restante -= 1
    return atual


def dias_uteis_restantes(hoje: date, vencimento: date, feriados: Iterable[date] = (),
                         suspensoes: Iterable[Suspensao] = ()) -> int:
    """Dias úteis entre hoje (exclusive) e o vencimento (inclusive); negativo se vencido."""
    fer, susp = frozenset(feriados), tuple(suspensoes)
    if vencimento < hoje:
        return -dias_uteis_restantes(vencimento, hoje, fer, susp)
    n, d = 0, hoje
    while d < vencimento:
        d += timedelta(days=1)
        if _conta(d, fer, susp):
            n += 1
    return n


def classificar(hoje: date, vencimento: date, feriados: Iterable[date] = (),
                suspensoes: Iterable[Suspensao] = ()) -> Alerta:
    if vencimento < hoje:
        return Alerta.VENCIDO
    if vencimento == hoje:
        return Alerta.HOJE
    r = dias_uteis_restantes(hoje, vencimento, feriados, suspensoes)
    if r <= 2:
        return Alerta.URGENTE
    if r <= 5:
        return Alerta.ATENCAO
    return Alerta.NORMAL


@dataclass(frozen=True)
class Prazo:
    processo: str
    descricao: str
    vencimento: date


def alertas(prazos: Iterable[Prazo], hoje: date, feriados: Iterable[date] = (),
            suspensoes: Iterable[Suspensao] = ()) -> list[tuple[Prazo, Alerta]]:
    """Prazos não normais, ordenados por vencimento."""
    fer, susp = frozenset(feriados), tuple(suspensoes)
    res = [(p, classificar(hoje, p.vencimento, fer, susp)) for p in prazos]
    return sorted(((p, a) for p, a in res if a != Alerta.NORMAL), key=lambda t: t[0].vencimento)


def prorrogar_se_nao_util(d: date, feriados: Iterable[date] = ()) -> date:
    """Se o vencimento cair em dia não útil, passa ao próximo dia útil."""
    fer = frozenset(feriados)
    return d if eh_dia_util(d, fer) else proximo_dia_util(d, fer)
