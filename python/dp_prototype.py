"""Prototype: clonagem de modelos de documento com cópia profunda."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field


@dataclass
class Documento:
    titulo: str
    secoes: list[str] = field(default_factory=list)
    metadados: dict[str, str] = field(default_factory=dict)

    def clonar(self, **alteracoes) -> "Documento":
        novo = copy.deepcopy(self)
        for k, v in alteracoes.items():
            if not hasattr(novo, k):
                raise AttributeError(k)
            setattr(novo, k, v)
        return novo


class RegistroModelos:
    def __init__(self) -> None:
        self._modelos: dict[str, Documento] = {}

    def registrar(self, nome: str, modelo: Documento) -> None:
        self._modelos[nome] = modelo.clonar()

    def criar(self, nome: str, **alteracoes) -> Documento:
        return self._modelos[nome].clonar(**alteracoes)
