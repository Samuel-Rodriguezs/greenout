"""Decorator (de objetos): cafeteria com adicionais empilháveis."""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class Bebida(ABC):
    @abstractmethod
    def descricao(self) -> str: ...

    @abstractmethod
    def preco(self) -> Decimal: ...


class Cafe(Bebida):
    def descricao(self) -> str:
        return "cafe"

    def preco(self) -> Decimal:
        return Decimal("5.00")


class Adicional(Bebida):
    nome = ""
    custo = Decimal("0")

    def __init__(self, bebida: Bebida) -> None:
        self._bebida = bebida

    def descricao(self) -> str:
        return f"{self._bebida.descricao()} + {self.nome}"

    def preco(self) -> Decimal:
        return self._bebida.preco() + self.custo


class Leite(Adicional):
    nome = "leite"
    custo = Decimal("1.50")


class Chantilly(Adicional):
    nome = "chantilly"
    custo = Decimal("2.25")


class Caramelo(Adicional):
    nome = "caramelo"
    custo = Decimal("1.00")
