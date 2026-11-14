"""State: ciclo de vida de um pedido (criado -> pago -> enviado -> entregue)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class EstadoInvalido(Exception):
    pass


class Estado(ABC):
    nome = ""

    def pagar(self, p: "Pedido") -> None:
        raise EstadoInvalido(f"não é possível pagar em '{self.nome}'")

    def enviar(self, p: "Pedido") -> None:
        raise EstadoInvalido(f"não é possível enviar em '{self.nome}'")

    def entregar(self, p: "Pedido") -> None:
        raise EstadoInvalido(f"não é possível entregar em '{self.nome}'")

    def cancelar(self, p: "Pedido") -> None:
        raise EstadoInvalido(f"não é possível cancelar em '{self.nome}'")


class Criado(Estado):
    nome = "criado"

    def pagar(self, p: "Pedido") -> None:
        p.estado = Pago()

    def cancelar(self, p: "Pedido") -> None:
        p.estado = Cancelado()


class Pago(Estado):
    nome = "pago"

    def enviar(self, p: "Pedido") -> None:
        p.estado = Enviado()

    def cancelar(self, p: "Pedido") -> None:
        p.estado = Cancelado()


class Enviado(Estado):
    nome = "enviado"

    def entregar(self, p: "Pedido") -> None:
        p.estado = Entregue()


class Entregue(Estado):
    nome = "entregue"


class Cancelado(Estado):
    nome = "cancelado"


class Pedido:
    def __init__(self) -> None:
        self.estado: Estado = Criado()

    @property
    def situacao(self) -> str:
        return self.estado.nome

    def pagar(self) -> None:
        self.estado.pagar(self)

    def enviar(self) -> None:
        self.estado.enviar(self)

    def entregar(self) -> None:
        self.estado.entregar(self)

    def cancelar(self) -> None:
        self.estado.cancelar(self)
