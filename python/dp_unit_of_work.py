"""Unit of Work: transferências bancárias confirmadas ou revertidas em bloco."""
from __future__ import annotations

from typing import Optional


class Banco:
    def __init__(self, saldos: dict[str, int]) -> None:
        self.saldos = dict(saldos)


class UnidadeDeTrabalho:
    def __init__(self, banco: Banco) -> None:
        self._banco = banco
        self._pendente: dict[str, int] = {}
        self._ativa = False

    def __enter__(self) -> "UnidadeDeTrabalho":
        self._pendente = dict(self._banco.saldos)
        self._ativa = True
        return self

    def saldo(self, conta: str) -> int:
        return self._pendente[conta]

    def transferir(self, origem: str, destino: str, valor: int) -> None:
        if valor <= 0:
            raise ValueError("valor deve ser positivo")
        if self._pendente[origem] < valor:
            raise ValueError("saldo insuficiente")
        self._pendente[origem] -= valor
        self._pendente[destino] += valor

    def __exit__(self, tipo, exc, tb) -> Optional[bool]:
        if tipo is None:
            self._banco.saldos = self._pendente  # commit
        self._pendente = {}
        self._ativa = False
        return None
