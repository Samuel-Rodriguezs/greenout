"""Parser e formatador de durações ISO-8601 (ex.: PT1H30M, P1DT12H, P2W)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta

_PADRAO = re.compile(
    r"^P(?:(?P<anos>\d+)Y)?(?:(?P<meses>\d+)M)?(?:(?P<semanas>\d+)W)?(?:(?P<dias>\d+)D)?"
    r"(?P<tempo>T(?:(?P<horas>\d+)H)?(?:(?P<minutos>\d+)M)?(?:(?P<segundos>\d+(?:[.,]\d+)?)S)?)?$"
)

DIAS_POR_ANO = 365
DIAS_POR_MES = 30


@dataclass(frozen=True)
class Duracao:
    anos: int = 0
    meses: int = 0
    semanas: int = 0
    dias: int = 0
    horas: int = 0
    minutos: int = 0
    segundos: float = 0.0

    def para_timedelta(self) -> timedelta:
        """Converte para timedelta; ano = 365 dias e mês = 30 dias (aproximação)."""
        return timedelta(
            days=self.anos * DIAS_POR_ANO + self.meses * DIAS_POR_MES + self.semanas * 7 + self.dias,
            hours=self.horas,
            minutes=self.minutos,
            seconds=self.segundos,
        )

    def total_segundos(self) -> float:
        return self.para_timedelta().total_seconds()

    def __str__(self) -> str:
        return formatar_duracao(self)


def parse_duracao(texto: str) -> Duracao:
    """Lê uma duração ISO-8601. Levanta ValueError se o texto for inválido."""
    casou = _PADRAO.match(texto.strip().upper())
    if casou is None or texto.strip().upper() in ("P", "PT"):
        raise ValueError(f"duração ISO-8601 inválida: {texto!r}")
    g = casou.groupdict()
    if g["tempo"] == "T" and not any((g["horas"], g["minutos"], g["segundos"])):
        raise ValueError(f"duração ISO-8601 inválida: {texto!r}")
    if not any(v for k, v in g.items() if k != "tempo" and v is not None):
        raise ValueError(f"duração ISO-8601 inválida: {texto!r}")
    return Duracao(
        anos=int(g["anos"] or 0),
        meses=int(g["meses"] or 0),
        semanas=int(g["semanas"] or 0),
        dias=int(g["dias"] or 0),
        horas=int(g["horas"] or 0),
        minutos=int(g["minutos"] or 0),
        segundos=float((g["segundos"] or "0").replace(",", ".")),
    )


def _numero(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def formatar_duracao(d: Duracao) -> str:
    """Forma canônica ISO-8601; duração zero vira PT0S."""
    data = "".join(
        f"{v}{s}" for v, s in ((d.anos, "Y"), (d.meses, "M"), (d.semanas, "W"), (d.dias, "D")) if v
    )
    tempo = "".join(
        f"{_numero(v)}{s}" for v, s in ((d.horas, "H"), (d.minutos, "M"), (d.segundos, "S")) if v
    )
    if not data and not tempo:
        return "PT0S"
    return "P" + data + ("T" + tempo if tempo else "")


def de_timedelta(td: timedelta) -> Duracao:
    """Converte timedelta não negativo em Duracao (dias, horas, minutos e segundos)."""
    if td < timedelta(0):
        raise ValueError("duração negativa não é suportada")
    total = td.total_seconds()
    dias, resto = divmod(total, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, segundos = divmod(resto, 60)
    return Duracao(dias=int(dias), horas=int(horas), minutos=int(minutos), segundos=segundos)
