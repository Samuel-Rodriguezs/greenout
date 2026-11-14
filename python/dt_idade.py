"""Idade exata (anos, meses e dias) entre uma data de nascimento e uma data de referência."""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Idade:
    anos: int
    meses: int
    dias: int

    def __str__(self) -> str:
        def parte(n: int, singular: str, plural: str) -> str:
            return f"{n} {singular if n == 1 else plural}"

        return ", ".join(
            [parte(self.anos, "ano", "anos"), parte(self.meses, "mês", "meses"), parte(self.dias, "dia", "dias")]
        )


def somar_meses(d: date, meses: int) -> date:
    """Soma meses a d; se o dia não existir no mês de destino, usa o último dia do mês."""
    indice = d.year * 12 + (d.month - 1) + meses
    ano, mes0 = divmod(indice, 12)
    mes = mes0 + 1
    dia = min(d.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def calcular_idade(nascimento: date, referencia: date | None = None) -> Idade:
    """Idade exata. Quem nasceu em 29/02 faz aniversário em 28/02 nos anos não bissextos."""
    ref = referencia if referencia is not None else date.today()
    if nascimento > ref:
        raise ValueError("a data de nascimento é posterior à data de referência")
    k = (ref.year - nascimento.year) * 12 + (ref.month - nascimento.month)
    while somar_meses(nascimento, k) > ref:
        k -= 1
    anos, meses = divmod(k, 12)
    return Idade(anos, meses, (ref - somar_meses(nascimento, k)).days)


def idade_em_anos(nascimento: date, referencia: date | None = None) -> int:
    return calcular_idade(nascimento, referencia).anos


def eh_maior_de_idade(nascimento: date, referencia: date | None = None, maioridade: int = 18) -> bool:
    return idade_em_anos(nascimento, referencia) >= maioridade
