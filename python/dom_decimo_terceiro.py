"""13º salário proporcional (avos de meses com 15 dias ou mais trabalhados)."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

CENTAVOS = Decimal("0.01")


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def avos_no_ano(ano: int, admissao: Optional[date] = None,
                demissao: Optional[date] = None) -> int:
    """Conta meses do ano em que houve 15 dias ou mais de vínculo."""
    inicio_ano, fim_ano = date(ano, 1, 1), date(ano, 12, 31)
    inicio = max(admissao, inicio_ano) if admissao else inicio_ano
    fim = min(demissao, fim_ano) if demissao else fim_ano
    if admissao and demissao and demissao < admissao:
        raise ValueError("demissão anterior à admissão")
    avos = 0
    for mes in range(1, 13):
        primeiro = date(ano, mes, 1)
        ultimo = date(ano, mes, calendar.monthrange(ano, mes)[1])
        ini, f = max(inicio, primeiro), min(fim, ultimo)
        if f >= ini and (f - ini).days + 1 >= 15:
            avos += 1
    return avos


def decimo_terceiro(salario: object, avos: int) -> Decimal:
    """Valor integral proporcional: salário * avos / 12."""
    if not 0 <= avos <= 12:
        raise ValueError("avos deve estar entre 0 e 12")
    sal = Decimal(str(salario))
    if sal < 0:
        raise ValueError("salário não pode ser negativo")
    return _q(sal * avos / 12)


def primeira_parcela(salario: object, avos: int) -> Decimal:
    """Adiantamento de 50% (sem descontos), pago até 30/11."""
    return _q(decimo_terceiro(salario, avos) / 2)


def segunda_parcela(salario: object, avos: int, inss: object = 0, irrf: object = 0) -> Decimal:
    """Total - primeira parcela - INSS - IRRF (descontos incidem na 2ª parcela)."""
    return (decimo_terceiro(salario, avos) - primeira_parcela(salario, avos)
            - Decimal(str(inss)) - Decimal(str(irrf)))
