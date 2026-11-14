"""Prazo prescricional trabalhista (exemplo didático: 5 anos na vigência, 2 após a extinção).

Os prazos são parâmetros; não substitui análise jurídica.
"""
from __future__ import annotations

import calendar
from datetime import date

PRAZO_QUINQUENAL = 5
PRAZO_BIENAL = 2


def somar_anos(data: date, anos: int) -> date:
    """Soma anos; 29/02 cai em 28/02 se o ano de destino não é bissexto."""
    ano = data.year + anos
    dia = min(data.day, calendar.monthrange(ano, data.month)[1])
    return date(ano, data.month, dia)


def limite_ajuizamento(extincao_contrato: date, anos: int = PRAZO_BIENAL) -> date:
    """Último dia para ajuizar após a extinção do contrato (prescrição bienal)."""
    return somar_anos(extincao_contrato, anos)


def bienal_prescrita(extincao_contrato: date, ajuizamento: date,
                     anos: int = PRAZO_BIENAL) -> bool:
    return ajuizamento > limite_ajuizamento(extincao_contrato, anos)


def inicio_periodo_exigivel(ajuizamento: date, anos: int = PRAZO_QUINQUENAL) -> date:
    """Data a partir da qual as parcelas ainda são exigíveis."""
    return somar_anos(ajuizamento, -anos)


def parcela_prescrita(data_exigibilidade: date, ajuizamento: date,
                      anos: int = PRAZO_QUINQUENAL) -> bool:
    """Prescrita se a exigibilidade é anterior ao quinquênio retroativo."""
    return data_exigibilidade < inicio_periodo_exigivel(ajuizamento, anos)
