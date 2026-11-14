"""Data por extenso em português: '14 de novembro de 2026' e variações."""
from __future__ import annotations

import re
from datetime import date

from dt_extenso import numero_por_extenso

MESES = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)
DIAS_SEMANA = (
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
)


def data_por_extenso(d: date, com_dia_semana: bool = False, numeros_por_extenso: bool = False) -> str:
    """
    - padrão: '14 de novembro de 2026' (dia 1 vira '1º');
    - com_dia_semana: 'sábado, 14 de novembro de 2026';
    - numeros_por_extenso: 'catorze de novembro de dois mil e vinte e seis' (dia 1 = 'primeiro').
    """
    if numeros_por_extenso:
        dia = "primeiro" if d.day == 1 else numero_por_extenso(d.day)
        ano = numero_por_extenso(d.year)
    else:
        dia = "1º" if d.day == 1 else str(d.day)
        ano = str(d.year)
    texto = f"{dia} de {MESES[d.month - 1]} de {ano}"
    if com_dia_semana:
        texto = f"{DIAS_SEMANA[d.weekday()]}, {texto}"
    return texto


_PADRAO = re.compile(
    r"^\s*(?:[^\d,]+,\s*)?(\d{1,2})º?\s+de\s+([a-zç]+)\s+de\s+(\d{1,4})\s*$", re.IGNORECASE
)


def parse_data_extenso(texto: str) -> date:
    """Lê '14 de novembro de 2026' (aceita '1º', dia da semana opcional e maiúsculas)."""
    casou = _PADRAO.match(texto)
    if casou is None:
        raise ValueError(f"data por extenso inválida: {texto!r}")
    nome = casou.group(2).lower()
    if nome not in MESES:
        raise ValueError(f"mês desconhecido: {nome!r}")
    return date(int(casou.group(3)), MESES.index(nome) + 1, int(casou.group(1)))
