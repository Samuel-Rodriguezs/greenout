"""Visitor: operações sobre uma árvore de expressões aritméticas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

R = TypeVar("R")


class Visitante(ABC, Generic[R]):
    @abstractmethod
    def visitar_numero(self, n: "Numero") -> R: ...

    @abstractmethod
    def visitar_soma(self, s: "Soma") -> R: ...

    @abstractmethod
    def visitar_produto(self, p: "Produto") -> R: ...


class Expr(ABC):
    @abstractmethod
    def aceitar(self, v: Visitante[R]) -> R: ...


class Numero(Expr):
    def __init__(self, valor: float) -> None:
        self.valor = valor

    def aceitar(self, v: Visitante[R]) -> R:
        return v.visitar_numero(self)


class Soma(Expr):
    def __init__(self, esq: Expr, dir_: Expr) -> None:
        self.esq, self.dir = esq, dir_

    def aceitar(self, v: Visitante[R]) -> R:
        return v.visitar_soma(self)


class Produto(Expr):
    def __init__(self, esq: Expr, dir_: Expr) -> None:
        self.esq, self.dir = esq, dir_

    def aceitar(self, v: Visitante[R]) -> R:
        return v.visitar_produto(self)


class Avaliador(Visitante[float]):
    def visitar_numero(self, n: Numero) -> float:
        return n.valor

    def visitar_soma(self, s: Soma) -> float:
        return s.esq.aceitar(self) + s.dir.aceitar(self)

    def visitar_produto(self, p: Produto) -> float:
        return p.esq.aceitar(self) * p.dir.aceitar(self)


class Impressor(Visitante[str]):
    def visitar_numero(self, n: Numero) -> str:
        return f"{n.valor:g}"

    def visitar_soma(self, s: Soma) -> str:
        return f"({s.esq.aceitar(self)} + {s.dir.aceitar(self)})"

    def visitar_produto(self, p: Produto) -> str:
        return f"{p.esq.aceitar(self)} * {p.dir.aceitar(self)}"


class ContadorNos(Visitante[int]):
    def visitar_numero(self, n: Numero) -> int:
        return 1

    def visitar_soma(self, s: Soma) -> int:
        return 1 + s.esq.aceitar(self) + s.dir.aceitar(self)

    def visitar_produto(self, p: Produto) -> int:
        return 1 + p.esq.aceitar(self) + p.dir.aceitar(self)
