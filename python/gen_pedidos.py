"""Pedidos de compra fictícios e coerentes: itens, totais em centavos e datas crescentes."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

CATALOGO: tuple[tuple[str, int], ...] = (
    ("Caderno universitário", 2490), ("Caneta esferográfica", 350), ("Mochila", 15990),
    ("Garrafa térmica", 7490), ("Fone de ouvido", 12900), ("Mouse sem fio", 5990),
    ("Teclado compacto", 18990), ("Luminária de mesa", 8990), ("Cabo USB-C", 2990),
    ("Agenda 2025", 3990),
)
STATUS: tuple[str, ...] = ("pago", "enviado", "entregue")


@dataclass(frozen=True)
class ItemPedido:
    produto: str
    preco_unitario: int
    quantidade: int

    @property
    def subtotal(self) -> int:
        return self.preco_unitario * self.quantidade


@dataclass(frozen=True)
class Pedido:
    numero: int
    cliente_id: int
    criado_em: datetime
    itens: tuple[ItemPedido, ...]
    desconto: int
    frete: int
    status: str

    @property
    def total(self) -> int:
        return sum(i.subtotal for i in self.itens) - self.desconto + self.frete


def gerar_pedido(
    rng: random.Random, numero: int, cliente_id: int, criado_em: datetime
) -> Pedido:
    produtos = rng.sample(CATALOGO, rng.randint(1, 4))
    itens = tuple(ItemPedido(nome, preco, rng.randint(1, 5)) for nome, preco in produtos)
    bruto = sum(i.subtotal for i in itens)
    desconto = round(bruto * rng.choice((0, 0, 5, 10)) / 100)
    frete = 0 if bruto - desconto >= 20000 else rng.choice((990, 1490, 1990))
    return Pedido(numero, cliente_id, criado_em, itens, desconto, frete, rng.choice(STATUS))


def gerar_pedidos(
    seed: int, n: int, inicio: datetime, n_clientes: int = 20
) -> list[Pedido]:
    """Pedidos numerados de 1..n com `criado_em` estritamente crescente."""
    if n_clientes < 1:
        raise ValueError("n_clientes deve ser >= 1")
    rng = random.Random(seed)
    t = inicio
    saida: list[Pedido] = []
    for numero in range(1, n + 1):
        t = t + timedelta(seconds=rng.randint(30, 6 * 3600))
        saida.append(gerar_pedido(rng, numero, rng.randint(1, n_clientes), t))
    return saida
