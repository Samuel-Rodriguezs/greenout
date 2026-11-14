"""Gilded Rose Kata (refatorado): atualização diária de qualidade dos itens.

Regras:
- Qualidade nunca é negativa nem passa de 50 (exceto Sulfuras, fixa em 80).
- Passada a validade, a degradação é dobrada.
- Aged Brie aumenta com o tempo.
- Backstage passes: +1; +2 com 10 dias ou menos; +3 com 5 ou menos; 0 após o show.
- Sulfuras nunca vende nem perde qualidade.
- Conjured degrada duas vezes mais rápido.
"""
from __future__ import annotations

from dataclasses import dataclass

BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
CONJURED_PREFIXO = "Conjured"


@dataclass
class Item:
    nome: str
    prazo: int
    qualidade: int


def _limitar(q: int) -> int:
    return max(0, min(50, q))


def _variacao(item: Item) -> int:
    """Variação de qualidade do dia, usando o prazo ANTES de decrementar."""
    if item.nome == BRIE:
        return 2 if item.prazo <= 0 else 1
    if item.nome == BACKSTAGE:
        if item.prazo <= 0:
            return -item.qualidade
        if item.prazo <= 5:
            return 3
        if item.prazo <= 10:
            return 2
        return 1
    base = -2 if item.prazo <= 0 else -1
    return base * 2 if item.nome.startswith(CONJURED_PREFIXO) else base


def atualizar_item(item: Item) -> None:
    if item.nome == SULFURAS:
        return
    item.qualidade = _limitar(item.qualidade + _variacao(item))
    item.prazo -= 1


def atualizar_qualidade(itens: list[Item]) -> None:
    for item in itens:
        atualizar_item(item)
