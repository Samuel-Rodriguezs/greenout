"""Parser de datas livres em português ("amanhã", "daqui a 3 dias", "próxima sexta"), com data base injetável."""
from __future__ import annotations

import calendar
import re
import unicodedata
from datetime import date, timedelta


class ErroData(ValueError):
    """Expressão de data não reconhecida."""


_MESES = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
          "setembro", "outubro", "novembro", "dezembro"]
_DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
_NUMS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
         "oito": 8, "nove": 9, "dez": 10, "quinze": 15, "vinte": 20, "trinta": 30}
_UNIDADES = {"dia": "d", "dias": "d", "semana": "s", "semanas": "s", "mes": "m", "meses": "m",
             "ano": "a", "anos": "a"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s)


def _somar_meses(d: date, n: int) -> date:
    idx = d.year * 12 + d.month - 1 + n
    ano, mes = divmod(idx, 12)
    mes += 1
    return date(ano, mes, min(d.day, calendar.monthrange(ano, mes)[1]))


def _deslocar(d: date, qtd: int, un: str) -> date:
    if un == "d":
        return d + timedelta(days=qtd)
    if un == "s":
        return d + timedelta(weeks=qtd)
    if un == "m":
        return _somar_meses(d, qtd)
    return _somar_meses(d, 12 * qtd)


def _mk(ano: int, mes: int, dia: int) -> date:
    try:
        return date(ano, mes, dia)
    except ValueError as e:
        raise ErroData(f"data inexistente: {dia:02d}/{mes:02d}/{ano}") from e


def _numero(tok: str) -> int:
    if tok.isdigit():
        return int(tok)
    if tok in _NUMS:
        return _NUMS[tok]
    raise ErroData(f"número desconhecido: {tok!r}")


def parse(texto: str, base: date | None = None) -> date:
    """Interpreta a expressão relativa à data `base` (padrão: hoje)."""
    base = base or date.today()
    t = re.sub(r"[- ]feira", "", _norm(texto))
    if not t:
        raise ErroData("expressão vazia")
    fixos = {"hoje": 0, "amanha": 1, "depois de amanha": 2, "ontem": -1, "anteontem": -2}
    if t in fixos:
        return base + timedelta(days=fixos[t])

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return _mk(*map(int, m.groups()))
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", t)
    if m:
        d, mes, ano = m.groups()
        return _mk(int(ano) if ano else base.year, int(mes), int(d))
    m = re.fullmatch(r"(?:dia )?(\d{1,2}) de (\w+)(?: de (\d{4}))?", t)
    if m and m.group(2) in _MESES:
        d, mes, ano = m.groups()
        return _mk(int(ano) if ano else base.year, _MESES.index(mes) + 1, int(d))

    m = re.fullmatch(r"(?:daqui a|em|dentro de) (\w+) (\w+)", t)
    if m and m.group(2) in _UNIDADES:
        return _deslocar(base, _numero(m.group(1)), _UNIDADES[m.group(2)])
    m = re.fullmatch(r"(?:ha )?(\w+) (\w+) atras", t) or re.fullmatch(r"ha (\w+) (\w+)", t)
    if m and m.group(2) in _UNIDADES:
        return _deslocar(base, -_numero(m.group(1)), _UNIDADES[m.group(2)])

    m = re.fullmatch(r"(proxim[oa]|ultim[oa]|passad[oa]|essa|esta|este|esse)? ?(\w+?)(?: (que vem|passada?|passado))?", t)
    if m:
        pref, nome, suf = m.groups()
        if nome in _DIAS:
            alvo = _DIAS.index(nome)
            if pref in ("ultimo", "ultima", "passado", "passada") or (suf or "").startswith("passad"):
                delta = (base.weekday() - alvo) % 7 or 7
                return base - timedelta(days=delta)
            if pref in ("proximo", "proxima") or suf == "que vem":
                delta = (alvo - base.weekday()) % 7 or 7
                return base + timedelta(days=delta)
            return base + timedelta(days=(alvo - base.weekday()) % 7)
        if nome in ("semana", "mes", "ano") and (pref or suf):
            un = {"semana": "s", "mes": "m", "ano": "a"}[nome]
            if pref in ("proximo", "proxima") or suf == "que vem":
                return _deslocar(base, 1, un)
            if pref in ("ultimo", "ultima", "passado", "passada") or (suf or "").startswith("passad"):
                return _deslocar(base, -1, un)
    raise ErroData(f"expressão não reconhecida: {texto!r}")
