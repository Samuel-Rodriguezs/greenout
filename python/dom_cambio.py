"""Conversor de moedas com cotação, spread e IOF (valores de exemplo, parametrizáveis).

Cotação = unidades de BRL por 1 unidade da moeda estrangeira.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def _d(valor: object) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _validar(valor: Decimal, cotacao: Decimal, spread: Decimal, iof: Decimal) -> None:
    if valor < 0:
        raise ValueError("valor não pode ser negativo")
    if cotacao <= 0:
        raise ValueError("cotação deve ser positiva")
    if not (0 <= spread < 1) or not (0 <= iof < 1):
        raise ValueError("spread e IOF devem estar em [0, 1)")


def comprar_moeda(brl: object, cotacao: object, spread: object = 0, iof: object = 0) -> Decimal:
    """Quanto de moeda estrangeira se obtém com `brl`.

    IOF incide sobre o valor em reais; a cotação de venda é cotação * (1 + spread).
    """
    v, c, s, i = _d(brl), _d(cotacao), _d(spread), _d(iof)
    _validar(v, c, s, i)
    liquido_brl = v - v * i
    return _q(liquido_brl / (c * (1 + s)))


def vender_moeda(valor_estrangeiro: object, cotacao: object, spread: object = 0,
                 iof: object = 0) -> Decimal:
    """Quanto de BRL se recebe ao vender moeda estrangeira.

    A cotação de compra é cotação * (1 - spread); o IOF incide sobre o BRL bruto.
    """
    v, c, s, i = _d(valor_estrangeiro), _d(cotacao), _d(spread), _d(iof)
    _validar(v, c, s, i)
    bruto = v * c * (1 - s)
    return _q(bruto - bruto * i)


def taxa_efetiva_compra(cotacao: object, spread: object = 0, iof: object = 0) -> Decimal:
    """BRL gastos por unidade estrangeira recebida, considerando spread e IOF."""
    c, s, i = _d(cotacao), _d(spread), _d(iof)
    _validar(Decimal(0), c, s, i)
    return c * (1 + s) / (1 - i)
