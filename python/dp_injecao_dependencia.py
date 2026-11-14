"""Injeção de dependência simples: contêiner com registro e resolução por tipo."""
from __future__ import annotations

import inspect
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class Container:
    def __init__(self) -> None:
        self._fabricas: dict[type, tuple[Callable[[], Any], bool]] = {}
        self._unicas: dict[type, Any] = {}

    def registrar(self, tipo: type, fabrica: Callable[[], Any] | type,
                  singleton: bool = False) -> None:
        if isinstance(fabrica, type):
            impl = fabrica
            fabrica = lambda: self.criar(impl)  # noqa: E731
        self._fabricas[tipo] = (fabrica, singleton)

    def resolver(self, tipo: type[T]) -> T:
        if tipo not in self._fabricas:
            return self.criar(tipo)
        fabrica, singleton = self._fabricas[tipo]
        if not singleton:
            return fabrica()
        if tipo not in self._unicas:
            self._unicas[tipo] = fabrica()
        return self._unicas[tipo]

    def criar(self, classe: type[T]) -> T:
        """Instancia classe resolvendo parâmetros do __init__ pelas anotações."""
        dicas = inspect.signature(classe.__init__).parameters
        args = {}
        for nome, p in dicas.items():
            if nome == "self" or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            if p.default is not p.empty:
                continue
            anot = p.annotation
            if isinstance(anot, str):
                anot = inspect.get_annotations(classe.__init__, eval_str=True)[nome]
            args[nome] = self.resolver(anot)
        return classe(**args)
