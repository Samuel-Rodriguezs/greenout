"""Conversão entre fusos horários com offsets fixos (sem horário de verão)."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

# Offsets fixos em minutos em relação ao UTC.
FUSOS: dict[str, int] = {
    "UTC": 0, "GMT": 0,
    "BRT": -180, "BRST": -120,
    "AMT": -240, "ACT": -300, "FNT": -120,
    "EST": -300, "EDT": -240, "CST": -360, "CDT": -300,
    "MST": -420, "MDT": -360, "PST": -480, "PDT": -420,
    "CET": 60, "CEST": 120, "EET": 120, "MSK": 180,
    "IST": 330, "JST": 540, "KST": 540, "AEST": 600,
}

_OFFSET = re.compile(r"^(?:UTC|GMT)?([+-])(\d{1,2})(?::?(\d{2}))?$")


def offset_em_minutos(fuso: str) -> int:
    """Aceita sigla conhecida (BRT) ou offset textual (+05:30, UTC-3, -0300)."""
    chave = fuso.strip().upper()
    if chave in FUSOS:
        return FUSOS[chave]
    casou = _OFFSET.match(chave)
    if casou is None:
        raise ValueError(f"fuso desconhecido: {fuso!r}")
    sinal = -1 if casou.group(1) == "-" else 1
    horas, minutos = int(casou.group(2)), int(casou.group(3) or 0)
    if horas > 14 or minutos > 59:
        raise ValueError(f"offset fora do intervalo: {fuso!r}")
    return sinal * (horas * 60 + minutos)


def para_tzinfo(fuso: str) -> timezone:
    return timezone(timedelta(minutes=offset_em_minutos(fuso)))


def converter(momento: datetime, origem: str, destino: str) -> datetime:
    """Converte um horário (ingênuo, interpretado em `origem`) para `destino`; resultado ingênuo."""
    if momento.tzinfo is not None:
        raise ValueError("passe um datetime ingênuo; o fuso de origem vem do argumento")
    delta = offset_em_minutos(destino) - offset_em_minutos(origem)
    return momento + timedelta(minutes=delta)


def com_fuso(momento: datetime, fuso: str) -> datetime:
    """Anexa o fuso a um datetime ingênuo."""
    if momento.tzinfo is not None:
        raise ValueError("o datetime já possui fuso")
    return momento.replace(tzinfo=para_tzinfo(fuso))


def formatar_offset(fuso: str) -> str:
    minutos = offset_em_minutos(fuso)
    sinal = "-" if minutos < 0 else "+"
    h, m = divmod(abs(minutos), 60)
    return f"{sinal}{h:02d}:{m:02d}"
