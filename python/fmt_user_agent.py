"""Parser simples de User-Agent: navegador, versão, sistema operacional e tipo de dispositivo."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UserAgent:
    navegador: str
    versao: str
    sistema: str
    dispositivo: str  # desktop, mobile, tablet, bot
    bot: bool


# A ordem importa: Edge/Opera/Chrome incluem "Chrome" e "Safari" na string.
_NAVEGADORES = [
    ("Edge", r"Edg(?:e|A|iOS)?/([\d.]+)"),
    ("Opera", r"(?:OPR|Opera)/([\d.]+)"),
    ("Firefox", r"(?:Firefox|FxiOS)/([\d.]+)"),
    ("Chrome", r"(?:Chrome|CriOS)/([\d.]+)"),
    ("Safari", r"Version/([\d.]+).*Safari/"),
    ("curl", r"curl/([\d.]+)"),
    ("Internet Explorer", r"(?:MSIE |rv:)([\d.]+)(?=.*Trident|;)"),
]

_SISTEMAS = [
    ("Windows", r"Windows NT ([\d.]+)"),
    ("Android", r"Android ([\d.]+)"),
    ("iOS", r"(?:iPhone|CPU) OS ([\d_]+)"),
    ("macOS", r"Mac OS X ([\d_.]+)"),
    ("Linux", r"(Linux)"),
]

_WIN = {"10.0": "10", "6.3": "8.1", "6.2": "8", "6.1": "7", "6.0": "Vista", "5.1": "XP"}


def parse(ua: str) -> UserAgent:
    """Interpreta a string de User-Agent; valores desconhecidos viram 'Desconhecido'."""
    bot = bool(re.search(r"bot|crawler|spider|slurp", ua, re.I))
    navegador, versao = "Desconhecido", ""
    if bot:
        m = re.search(r"([A-Za-z]*(?:bot|crawler|spider|slurp))[/ ]?([\d.]*)", ua, re.I)
        if m:
            navegador, versao = m.group(1), m.group(2)
    else:
        for nome, padrao in _NAVEGADORES:
            m = re.search(padrao, ua)
            if m:
                navegador, versao = nome, m.group(1)
                break
    sistema = "Desconhecido"
    for nome, padrao in _SISTEMAS:
        m = re.search(padrao, ua)
        if m:
            sistema = nome
            if nome == "Windows":
                sistema = "Windows " + _WIN.get(m.group(1), m.group(1))
            elif nome in ("Android", "iOS", "macOS"):
                sistema = f"{nome} {m.group(1).replace('_', '.')}"
            break
    if bot:
        disp = "bot"
    elif re.search(r"iPad|Tablet", ua) or ("Android" in ua and "Mobile" not in ua):
        disp = "tablet"
    elif re.search(r"Mobile|iPhone", ua):
        disp = "mobile"
    else:
        disp = "desktop"
    return UserAgent(navegador, versao, sistema, disp, bot)
