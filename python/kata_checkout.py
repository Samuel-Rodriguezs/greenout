"""Checkout Kata: caixa com regras de preço promocionais (centavos)."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Promocao:
    """Leve `quantidade` por `preco_total` (ex.: 3 por 130)."""
    quantidade: int
    preco_total: int


class Checkout:
    def __init__(self, precos: dict[str, int],
                 promocoes: dict[str, Promocao] | None = None,
                 leve_n_pague_m: dict[str, tuple[int, int]] | None = None) -> None:
        if any(p < 0 for p in precos.values()):
            raise ValueError("preço não pode ser negativo")
        self.precos = precos
        self.promocoes = promocoes or {}
        self.leve_n_pague_m = leve_n_pague_m or {}
        self.itens: Counter[str] = Counter()

    def scan(self, item: str) -> "Checkout":
        if item not in self.precos:
            raise KeyError(f"item desconhecido: {item}")
        self.itens[item] += 1
        return self

    def _total_item(self, item: str, qtd: int) -> int:
        preco = self.precos[item]
        if item in self.promocoes:
            promo = self.promocoes[item]
            lotes, resto = divmod(qtd, promo.quantidade)
            return lotes * promo.preco_total + resto * preco
        if item in self.leve_n_pague_m:
            leve, pague = self.leve_n_pague_m[item]
            lotes, resto = divmod(qtd, leve)
            return (lotes * pague + resto) * preco
        return qtd * preco

    def total(self) -> int:
        return sum(self._total_item(i, q) for i, q in self.itens.items())


def total(precos: dict[str, int], promocoes: dict[str, Promocao], itens: str) -> int:
    """Atalho: calcula o total para uma string como 'ABBAB'."""
    caixa = Checkout(precos, promocoes)
    for i in itens:
        caixa.scan(i)
    return caixa.total()
