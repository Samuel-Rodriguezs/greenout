"""Rescisão simplificada sem justa causa (didática; não substitui o TRCT).

Inclui aviso prévio proporcional (30 dias + 3 por ano completo, máx. 90),
saldo de salário, 13º e férias proporcionais (+1/3) e multa de 40% do FGTS.
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _somar_meses(data: date, meses: int) -> date:
    indice = data.year * 12 + data.month - 1 + meses
    ano, mes = divmod(indice, 12)
    mes += 1
    return date(ano, mes, min(data.day, calendar.monthrange(ano, mes)[1]))


def meses_completos(inicio: date, fim: date) -> int:
    """Meses inteiros entre duas datas (fim exclusivo do mês incompleto)."""
    if fim < inicio:
        raise ValueError("data final anterior à inicial")
    meses = (fim.year - inicio.year) * 12 + fim.month - inicio.month
    if _somar_meses(inicio, meses) > fim:
        meses -= 1
    return meses


def anos_completos(admissao: date, demissao: date) -> int:
    return meses_completos(admissao, demissao) // 12


def dias_aviso_previo(admissao: date, demissao: date) -> int:
    return min(30 + 3 * anos_completos(admissao, demissao), 90)


def _avos_decimo(ano: int, demissao: date) -> int:
    avos = 0
    for mes in range(1, demissao.month + 1):
        dias = demissao.day if mes == demissao.month else calendar.monthrange(ano, mes)[1]
        if dias >= 15:
            avos += 1
    return avos


def _avos_ferias(admissao: date, demissao: date) -> int:
    meses = meses_completos(admissao, demissao) % 12
    ancora = _somar_meses(admissao, meses_completos(admissao, demissao) - meses)
    resto = (demissao - _somar_meses(ancora, meses)).days
    return min(meses + (1 if resto >= 15 else 0), 12)


@dataclass(frozen=True)
class Rescisao:
    saldo_salario: Decimal
    aviso_previo: Decimal
    decimo_terceiro: Decimal
    ferias_proporcionais: Decimal
    multa_fgts: Decimal
    total: Decimal


def rescisao_sem_justa_causa(salario: object, admissao: date, demissao: date,
                             saldo_fgts: object = 0,
                             aviso_indenizado: bool = True,
                             multa: Decimal = Decimal("0.40")) -> Rescisao:
    """Calcula verbas brutas (sem INSS/IRRF); aviso não projeta avos (simplificação)."""
    sal = Decimal(str(salario))
    if sal < 0:
        raise ValueError("salário não pode ser negativo")
    if demissao < admissao:
        raise ValueError("demissão anterior à admissão")
    dia = sal / 30
    saldo = _q(dia * min(demissao.day, 30))
    aviso = _q(dia * dias_aviso_previo(admissao, demissao)) if aviso_indenizado else Decimal("0.00")
    avos13 = _avos_decimo(demissao.year, demissao)
    if admissao.year == demissao.year:
        avos13 = 0
        for mes in range(admissao.month, demissao.month + 1):
            ini = admissao.day if mes == admissao.month else 1
            fim = demissao.day if mes == demissao.month else calendar.monthrange(demissao.year, mes)[1]
            if fim - ini + 1 >= 15:
                avos13 += 1
    decimo = _q(sal * avos13 / 12)
    base_ferias = sal * _avos_ferias(admissao, demissao) / 12
    ferias = _q(base_ferias) + _q(base_ferias / 3)
    multa_fgts = _q(Decimal(str(saldo_fgts)) * multa)
    total = saldo + aviso + decimo + ferias + multa_fgts
    return Rescisao(saldo, aviso, decimo, ferias, multa_fgts, total)
