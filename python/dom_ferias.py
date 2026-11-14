"""Férias com adicional de 1/3 constitucional, abono pecuniário e proporcionais."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")

# (máximo de faltas injustificadas, dias de férias) - regra da CLT (art. 130).
TABELA_FALTAS = ((5, 30), (14, 24), (23, 18), (32, 12))


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Ferias:
    dias_gozados: int
    valor_ferias: Decimal
    terco: Decimal
    abono: Decimal
    terco_abono: Decimal
    total: Decimal


def dias_de_direito(faltas_injustificadas: int) -> int:
    """Dias de férias conforme faltas no período aquisitivo."""
    if faltas_injustificadas < 0:
        raise ValueError("faltas não pode ser negativo")
    for maximo, dias in TABELA_FALTAS:
        if faltas_injustificadas <= maximo:
            return dias
    return 0


def calcular_ferias(salario: object, dias_direito: int = 30,
                    dias_vendidos: int = 0) -> Ferias:
    """Salário/30 por dia gozado, +1/3. Abono: até 1/3 dos dias, também com 1/3."""
    sal = _d(salario)
    if sal < 0:
        raise ValueError("salário não pode ser negativo")
    if not 0 <= dias_direito <= 30:
        raise ValueError("dias de direito deve estar entre 0 e 30")
    if dias_vendidos < 0 or dias_vendidos > dias_direito // 3:
        raise ValueError("abono pecuniário limitado a 1/3 dos dias de direito")
    dia = sal / 30
    gozados = dias_direito - dias_vendidos
    valor = _q(dia * gozados)
    terco = _q(dia * gozados / 3)
    abono = _q(dia * dias_vendidos)
    terco_abono = _q(dia * dias_vendidos / 3)
    return Ferias(gozados, valor, terco, abono, terco_abono,
                  valor + terco + abono + terco_abono)


def ferias_proporcionais(salario: object, avos: int) -> Decimal:
    """Férias proporcionais + 1/3: salário * avos/12 * 4/3."""
    if not 0 <= avos <= 12:
        raise ValueError("avos deve estar entre 0 e 12")
    base = _d(salario) * avos / 12
    return _q(base) + _q(base / 3)
