"""Sistema de inventario com OOP: produtos, estoque e relatorios."""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Produto:
    sku: str
    nome: str
    preco: float
    quantidade: int = 0
    minimo: int = 0

    def __post_init__(self) -> None:
        if self.preco < 0 or self.quantidade < 0 or self.minimo < 0:
            raise ValueError("valores negativos nao permitidos")

    @property
    def valor_total(self) -> float:
        return self.preco * self.quantidade


class Inventario:
    def __init__(self) -> None:
        self._produtos: Dict[str, Produto] = {}

    def cadastrar(self, produto: Produto) -> None:
        if produto.sku in self._produtos:
            raise ValueError(f"sku duplicado: {produto.sku}")
        self._produtos[produto.sku] = produto

    def _get(self, sku: str) -> Produto:
        if sku not in self._produtos:
            raise KeyError(f"sku desconhecido: {sku}")
        return self._produtos[sku]

    def entrada(self, sku: str, qtd: int) -> None:
        if qtd <= 0:
            raise ValueError("quantidade deve ser positiva")
        self._get(sku).quantidade += qtd

    def saida(self, sku: str, qtd: int) -> None:
        if qtd <= 0:
            raise ValueError("quantidade deve ser positiva")
        p = self._get(sku)
        if qtd > p.quantidade:
            raise ValueError("estoque insuficiente")
        p.quantidade -= qtd

    def abaixo_do_minimo(self) -> List[Produto]:
        return sorted(
            (p for p in self._produtos.values() if p.quantidade < p.minimo),
            key=lambda p: p.sku,
        )

    def valor_total(self) -> float:
        return sum(p.valor_total for p in self._produtos.values())
