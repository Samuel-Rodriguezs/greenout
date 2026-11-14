"""Parser de expressões cron de 5 campos e cálculo da próxima execução.

Formato: minuto hora dia-do-mês mês dia-da-semana. Suporta *, listas (1,2), faixas (1-5),
passos (*/15, 10-30/5), nomes de meses (jan..dez) e de dias (dom..sab). Dia da semana 0 e 7 = domingo.
Como no cron clássico, se dia-do-mês e dia-da-semana forem ambos restritos, vale um OU o outro.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

_MESES = {n: i for i, n in enumerate(("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"), 1)}
_MESES.update({"feb": 2, "apr": 4, "may": 5, "aug": 8, "sep": 9, "oct": 10, "dec": 12})
_DIAS = {"dom": 0, "seg": 1, "ter": 2, "qua": 3, "qui": 4, "sex": 5, "sab": 6,
         "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}


def _valor(token: str, nomes: dict[str, int]) -> int:
    t = token.lower()
    if t in nomes:
        return nomes[t]
    if not t.isdigit():
        raise ValueError(f"valor cron inválido: {token!r}")
    return int(t)


def _campo(texto: str, minimo: int, maximo: int, nomes: dict[str, int] | None = None) -> frozenset[int]:
    nomes = nomes or {}
    valores: set[int] = set()
    for parte in texto.split(","):
        if not parte:
            raise ValueError("campo cron vazio")
        base, _, passo_txt = parte.partition("/")
        passo = 1
        if "/" in parte:
            if not passo_txt.isdigit() or int(passo_txt) < 1:
                raise ValueError(f"passo inválido: {parte!r}")
            passo = int(passo_txt)
        if base == "*":
            inicio, fim = minimo, maximo
        elif "-" in base:
            a, _, b = base.partition("-")
            inicio, fim = _valor(a, nomes), _valor(b, nomes)
        else:
            inicio = _valor(base, nomes)
            fim = maximo if "/" in parte else inicio
        if inicio > fim or inicio < minimo or fim > maximo:
            raise ValueError(f"valor fora da faixa {minimo}-{maximo}: {parte!r}")
        valores.update(range(inicio, fim + 1, passo))
    return frozenset(valores)


@dataclass(frozen=True)
class Cron:
    minutos: frozenset[int]
    horas: frozenset[int]
    dias_mes: frozenset[int]
    meses: frozenset[int]
    dias_semana: frozenset[int]  # 0 = domingo
    dia_mes_livre: bool
    dia_semana_livre: bool

    def dia_casa(self, d: datetime) -> bool:
        dow = (d.weekday() + 1) % 7  # converte para 0 = domingo
        no_mes = d.day in self.dias_mes
        na_semana = dow in self.dias_semana
        if self.dia_mes_livre and self.dia_semana_livre:
            return True
        if self.dia_mes_livre:
            return na_semana
        if self.dia_semana_livre:
            return no_mes
        return no_mes or na_semana

    def casa(self, d: datetime) -> bool:
        return (
            d.minute in self.minutos
            and d.hour in self.horas
            and d.month in self.meses
            and self.dia_casa(d)
        )

    def proxima(self, apos: datetime) -> datetime:
        """Próximo instante (estritamente depois de `apos`, sem segundos) que casa com a expressão."""
        atual = apos.replace(second=0, microsecond=0) + timedelta(minutes=1)
        limite = atual.year + 8  # cobre 29/02 e combinações raras
        while atual.year <= limite:
            if atual.month not in self.meses or not self.dia_casa(atual):
                atual = (atual + timedelta(days=1)).replace(hour=0, minute=0)
                continue
            if atual.hour not in self.horas:
                atual = (atual + timedelta(hours=1)).replace(minute=0)
                continue
            if atual.minute not in self.minutos:
                atual += timedelta(minutes=1)
                continue
            return atual
        raise ValueError("a expressão cron nunca é satisfeita")

    def proximas(self, apos: datetime, quantidade: int) -> list[datetime]:
        resultado: list[datetime] = []
        atual = apos
        for _ in range(quantidade):
            atual = self.proxima(atual)
            resultado.append(atual)
        return resultado


def parse_cron(expressao: str) -> Cron:
    campos = expressao.split()
    if len(campos) != 5:
        raise ValueError("expressão cron precisa de 5 campos")
    minutos = _campo(campos[0], 0, 59)
    horas = _campo(campos[1], 0, 23)
    dias_mes = _campo(campos[2], 1, 31)
    meses = _campo(campos[3], 1, 12, _MESES)
    dias_semana = frozenset(d % 7 for d in _campo(campos[4], 0, 7, _DIAS))
    return Cron(
        minutos, horas, dias_mes, meses, dias_semana,
        dia_mes_livre=campos[2].startswith("*"),
        dia_semana_livre=campos[4].startswith("*"),
    )


def proxima_execucao(expressao: str, apos: datetime) -> datetime:
    return parse_cron(expressao).proxima(apos)
