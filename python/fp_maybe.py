"""Mônada Maybe (Option): Just/Nothing com functor, applicative e monad."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Union


@dataclass(frozen=True)
class Just:
    valor: Any

    def map(self, f: Callable[[Any], Any]) -> "Maybe":
        return Just(f(self.valor))

    def bind(self, f: Callable[[Any], "Maybe"]) -> "Maybe":
        return f(self.valor)

    def ap(self, outro: "Maybe") -> "Maybe":
        """Aplica a função contida em self ao valor de `outro`."""
        return outro.map(self.valor)

    def get_or(self, padrao: Any) -> Any:
        return self.valor

    def eh_just(self) -> bool:
        return True


@dataclass(frozen=True)
class Nothing:
    def map(self, f: Callable[[Any], Any]) -> "Maybe":
        return self

    def bind(self, f: Callable[[Any], "Maybe"]) -> "Maybe":
        return self

    def ap(self, outro: "Maybe") -> "Maybe":
        return self

    def get_or(self, padrao: Any) -> Any:
        return padrao

    def eh_just(self) -> bool:
        return False


NADA = Nothing()
Maybe = Union[Just, Nothing]


def unit(valor: Any) -> Maybe:
    return Just(valor)


def de_optional(valor: Optional[Any]) -> Maybe:
    return NADA if valor is None else Just(valor)


def para_optional(m: Maybe) -> Optional[Any]:
    return m.valor if isinstance(m, Just) else None


def filtrar(m: Maybe, predicado: Callable[[Any], bool]) -> Maybe:
    return m.bind(lambda v: Just(v) if predicado(v) else NADA)


def ou_else(m: Maybe, alternativa: Maybe) -> Maybe:
    return m if isinstance(m, Just) else alternativa


def sequence(ms: Iterable[Maybe]) -> Maybe:
    """Lista de Maybe -> Maybe de lista (Nothing se algum for Nothing)."""
    valores = []
    for m in ms:
        if not isinstance(m, Just):
            return NADA
        valores.append(m.valor)
    return Just(valores)


def traverse(f: Callable[[Any], Maybe], itens: Iterable[Any]) -> Maybe:
    return sequence(f(x) for x in itens)


def lift2(f: Callable[[Any, Any], Any], a: Maybe, b: Maybe) -> Maybe:
    return Just(lambda x: lambda y: f(x, y)).ap(a).ap(b)
