"""Descritor de campo validado e classe com __slots__."""
from typing import Any, Callable, Optional


class Campo:
    """Descritor de dados que valida o valor na atribuição."""

    def __init__(self, validador: Callable[[Any], bool], mensagem: str = "valor inválido") -> None:
        self._validador = validador
        self._mensagem = mensagem
        self._nome = ""

    def __set_name__(self, dono: type, nome: str) -> None:
        self._nome = "_" + nome

    def __get__(self, instancia: Optional[object], dono: type):
        if instancia is None:
            return self
        try:
            return getattr(instancia, self._nome)
        except AttributeError:
            raise AttributeError(self._nome[1:]) from None

    def __set__(self, instancia: object, valor: Any) -> None:
        if not self._validador(valor):
            raise ValueError(f"{self._nome[1:]}: {self._mensagem} ({valor!r})")
        setattr(instancia, self._nome, valor)


def _numerico(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Ponto:
    __slots__ = ("_x", "_y")
    x = Campo(_numerico, "deve ser numérico")
    y = Campo(_numerico, "deve ser numérico")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Ponto({self.x}, {self.y})"
