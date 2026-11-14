"""Chain of Responsibility: aprovação de despesas por alçada."""
from __future__ import annotations

from typing import Optional


class Aprovador:
    def __init__(self, cargo: str, limite: float) -> None:
        self.cargo = cargo
        self.limite = limite
        self._proximo: Optional["Aprovador"] = None

    def encadear(self, proximo: "Aprovador") -> "Aprovador":
        self._proximo = proximo
        return proximo

    def aprovar(self, valor: float) -> str:
        if valor <= self.limite:
            return self.cargo
        if self._proximo is None:
            raise ValueError(f"valor {valor} acima de qualquer alçada")
        return self._proximo.aprovar(valor)


def cadeia_padrao() -> Aprovador:
    gerente = Aprovador("gerente", 1000)
    gerente.encadear(Aprovador("diretor", 10000)).encadear(Aprovador("presidente", 100000))
    return gerente
