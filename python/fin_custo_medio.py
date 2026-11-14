"""Preço médio ponderado e custo médio de uma posição (compras, vendas, lucro)."""
from __future__ import annotations


def preco_medio_ponderado(lotes: list[tuple[float, float]]) -> float:
    """Média ponderada de preços; cada lote é (quantidade, preço)."""
    total = sum(q for q, _ in lotes)
    if total <= 0:
        raise ValueError("quantidade total deve ser positiva")
    return sum(q * p for q, p in lotes) / total


class Posicao:
    """Posição em um ativo com custo médio. Taxas de compra entram no custo;
    taxas de venda reduzem o lucro realizado."""

    def __init__(self) -> None:
        self.quantidade = 0.0
        self.custo_total = 0.0
        self.lucro_realizado = 0.0

    @property
    def custo_medio(self) -> float:
        return self.custo_total / self.quantidade if self.quantidade else 0.0

    def comprar(self, quantidade: float, preco: float, taxa: float = 0.0) -> None:
        if quantidade <= 0 or preco <= 0 or taxa < 0:
            raise ValueError("quantidade e preço devem ser positivos; taxa >= 0")
        self.quantidade += quantidade
        self.custo_total += quantidade * preco + taxa

    def vender(self, quantidade: float, preco: float, taxa: float = 0.0) -> float:
        """Devolve o lucro realizado na venda."""
        if quantidade <= 0 or preco <= 0 or taxa < 0:
            raise ValueError("quantidade e preço devem ser positivos; taxa >= 0")
        if quantidade > self.quantidade:
            raise ValueError("venda maior que a posição")
        medio = self.custo_medio
        lucro = quantidade * (preco - medio) - taxa
        self.quantidade -= quantidade
        self.custo_total = medio * self.quantidade if self.quantidade else 0.0
        self.lucro_realizado += lucro
        return lucro

    def lucro_nao_realizado(self, preco_atual: float) -> float:
        return self.quantidade * (preco_atual - self.custo_medio)
