"""Facade: pedido de e-commerce escondendo estoque, pagamento e frete."""
from __future__ import annotations


class Estoque:
    def __init__(self, itens: dict[str, int]) -> None:
        self.itens = dict(itens)

    def reservar(self, sku: str, qtd: int) -> bool:
        if self.itens.get(sku, 0) < qtd:
            return False
        self.itens[sku] -= qtd
        return True

    def devolver(self, sku: str, qtd: int) -> None:
        self.itens[sku] = self.itens.get(sku, 0) + qtd


class Pagamento:
    def __init__(self, saldo: float) -> None:
        self.saldo = saldo

    def cobrar(self, valor: float) -> bool:
        if self.saldo < valor:
            return False
        self.saldo -= valor
        return True


class Frete:
    def calcular(self, qtd: int) -> float:
        return 10.0 + 2.0 * qtd


class LojaFacade:
    def __init__(self, estoque: Estoque, pagamento: Pagamento, frete: Frete) -> None:
        self._estoque = estoque
        self._pagamento = pagamento
        self._frete = frete

    def comprar(self, sku: str, qtd: int, preco_unit: float) -> str:
        if not self._estoque.reservar(sku, qtd):
            return "sem estoque"
        total = preco_unit * qtd + self._frete.calcular(qtd)
        if not self._pagamento.cobrar(total):
            self._estoque.devolver(sku, qtd)
            return "pagamento recusado"
        return f"pedido confirmado: {total:.2f}"
