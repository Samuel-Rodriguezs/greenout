"""Desconto de duplicata (desconto comercial/bancário simples).

Taxa mensal e IOF são parâmetros de exemplo (IOF = adicional fixo + alíquota
diária * dias).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Desconto:
    valor_face: Decimal
    desconto: Decimal
    iof: Decimal
    tarifa: Decimal
    liquido: Decimal
    taxa_efetiva_periodo: Decimal


def descontar_duplicata(valor_face: object, taxa_mensal: object, dias: int,
                        iof_diario: object = 0, iof_adicional: object = 0,
                        tarifa: object = 0) -> Desconto:
    """Desconto = face * taxa/30 * dias; líquido = face - desconto - IOF - tarifa."""
    face, taxa = _d(valor_face), _d(taxa_mensal)
    if face <= 0 or taxa < 0 or dias < 0:
        raise ValueError("face deve ser positiva; taxa e dias não negativos")
    desc = _q(face * taxa / 30 * dias)
    iof = _q(face * (_d(iof_diario) * dias + _d(iof_adicional)))
    tar = _q(_d(tarifa))
    liquido = _q(face) - desc - iof - tar
    if liquido <= 0:
        raise ValueError("líquido não positivo: encargos superam o valor de face")
    efetiva = (_q(face) / liquido) - 1
    return Desconto(_q(face), desc, iof, tar, liquido, efetiva)
