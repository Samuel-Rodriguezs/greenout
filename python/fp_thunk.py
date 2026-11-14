"""Avaliação preguiçosa: thunks com call-by-need (memoizado) e call-by-name."""
from __future__ import annotations

import functools
from typing import Any, Callable, Optional

_NAO_AVALIADO = object()
_EM_AVALIACAO = object()


class ErroCiclo(RuntimeError):
    """Um thunk dependeu do próprio valor durante a avaliação."""


class Thunk:
    """Call-by-need: o cálculo roda no máximo uma vez; o resultado é guardado."""

    __slots__ = ("_fn", "_valor")

    def __init__(self, fn: Callable[[], Any]):
        self._fn: Optional[Callable[[], Any]] = fn
        self._valor: Any = _NAO_AVALIADO

    @staticmethod
    def de_valor(valor: Any) -> "Thunk":
        t = Thunk(lambda: valor)
        t._valor = valor
        t._fn = None
        return t

    @property
    def avaliado(self) -> bool:
        return self._valor is not _NAO_AVALIADO and self._valor is not _EM_AVALIACAO

    def forcar(self) -> Any:
        if self._valor is _EM_AVALIACAO:
            raise ErroCiclo("dependência circular em thunk")
        if self._valor is _NAO_AVALIADO:
            fn = self._fn
            self._valor = _EM_AVALIACAO
            try:
                self._valor = fn()
            except BaseException:
                self._valor = _NAO_AVALIADO  # permite nova tentativa
                raise
            self._fn = None
        return self._valor

    def map(self, f: Callable[[Any], Any]) -> "Thunk":
        return Thunk(lambda: f(self.forcar()))

    def bind(self, f: Callable[[Any], "Thunk"]) -> "Thunk":
        return Thunk(lambda: f(self.forcar()).forcar())


class PorNome:
    """Call-by-name: reavalia a cada uso (útil para contrastar com Thunk)."""

    __slots__ = ("_fn", "avaliacoes")

    def __init__(self, fn: Callable[[], Any]):
        self._fn = fn
        self.avaliacoes = 0

    def forcar(self) -> Any:
        self.avaliacoes += 1
        return self._fn()


def forcar(x: Any) -> Any:
    """Força thunks (inclusive aninhados); outros valores passam direto."""
    while isinstance(x, (Thunk, PorNome)):
        x = x.forcar()
    return x


def preguicoso(f: Callable[..., Any]) -> Callable[..., Thunk]:
    """Decorador: a chamada devolve um Thunk e só calcula ao forçar."""
    @functools.wraps(f)
    def envolvida(*args: Any, **kwargs: Any) -> Thunk:
        return Thunk(lambda: f(*args, **kwargs))
    return envolvida


def se(condicao: Any, entao: Any, senao: Any) -> Any:
    """if como função: só o ramo escolhido é avaliado."""
    return forcar(entao) if forcar(condicao) else forcar(senao)


def e_(a: Any, b: Any) -> bool:
    """Conjunção com curto-circuito sobre thunks."""
    return bool(forcar(a)) and bool(forcar(b))


def ou_(a: Any, b: Any) -> bool:
    return bool(forcar(a)) or bool(forcar(b))


def propriedade_preguicosa(f: Callable[[Any], Any]) -> property:
    """Atributo calculado na primeira leitura e guardado na instância."""
    nome = "_lazy_" + f.__name__

    @property
    @functools.wraps(f)
    def prop(self: Any) -> Any:
        if nome not in self.__dict__:
            self.__dict__[nome] = f(self)
        return self.__dict__[nome]
    return prop
