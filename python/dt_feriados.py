"""Feriados nacionais do Brasil (fixos e móveis) por ano."""
from __future__ import annotations

from datetime import date, timedelta

from dt_pascoa import pascoa

_FIXOS: tuple[tuple[int, int, str], ...] = (
    (1, 1, "Confraternização Universal"),
    (4, 21, "Tiradentes"),
    (5, 1, "Dia do Trabalho"),
    (9, 7, "Independência do Brasil"),
    (10, 12, "Nossa Senhora Aparecida"),
    (11, 2, "Finados"),
    (11, 15, "Proclamação da República"),
    (12, 25, "Natal"),
)

# Dia da Consciência Negra é feriado nacional desde a Lei 14.759/2023 (vigência em 2024).
_ANO_CONSCIENCIA_NEGRA = 2024


def carnaval(ano: int) -> tuple[date, date]:
    """Segunda e terça-feira de Carnaval (48 e 47 dias antes da Páscoa)."""
    p = pascoa(ano)
    return p - timedelta(days=48), p - timedelta(days=47)


def sexta_feira_santa(ano: int) -> date:
    return pascoa(ano) - timedelta(days=2)


def corpus_christi(ano: int) -> date:
    return pascoa(ano) + timedelta(days=60)


def feriados_fixos(ano: int) -> dict[date, str]:
    resultado = {date(ano, m, d): nome for m, d, nome in _FIXOS}
    if ano >= _ANO_CONSCIENCIA_NEGRA:
        resultado[date(ano, 11, 20)] = "Dia da Consciência Negra"
    return resultado


def feriados_moveis(ano: int) -> dict[date, str]:
    """Feriado móvel oficial: Sexta-feira Santa."""
    return {sexta_feira_santa(ano): "Sexta-feira Santa"}


def pontos_facultativos(ano: int) -> dict[date, str]:
    """Pontos facultativos móveis: Carnaval e Corpus Christi."""
    seg, ter = carnaval(ano)
    return {
        seg: "Carnaval (segunda-feira)",
        ter: "Carnaval (terça-feira)",
        corpus_christi(ano): "Corpus Christi",
    }


def feriados_nacionais(ano: int, incluir_facultativos: bool = False) -> dict[date, str]:
    """Todos os feriados nacionais do ano, ordenados por data."""
    todos = {**feriados_fixos(ano), **feriados_moveis(ano)}
    if incluir_facultativos:
        todos.update(pontos_facultativos(ano))
    return dict(sorted(todos.items()))


def eh_feriado(d: date, incluir_facultativos: bool = False) -> bool:
    return d in feriados_nacionais(d.year, incluir_facultativos)
