"""Composição point-free: compose, pipe e um wrapper com operadores."""
from __future__ import annotations

from functools import reduce
from typing import Any, Callable, Iterable


def identidade(x: Any) -> Any:
    return x


def constante(valor: Any) -> Callable[..., Any]:
    return lambda *_a, **_k: valor


def compose(*fs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """compose(f, g, h)(x) == f(g(h(x)))."""
    return lambda x: reduce(lambda acc, f: f(acc), reversed(fs), x)


def pipe(*fs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """pipe(f, g, h)(x) == h(g(f(x)))."""
    return lambda x: reduce(lambda acc, f: f(acc), fs, x)


def canalizar(valor: Any, *fs: Callable[[Any], Any]) -> Any:
    """Aplica o valor ao pipe imediatamente."""
    return pipe(*fs)(valor)


class Fn:
    """Função com `>>` (esquerda para direita), `<<` (direita para esquerda) e `|`."""

    __slots__ = ("_f",)

    def __init__(self, f: Callable[..., Any]):
        self._f = f

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._f(*args, **kwargs)

    def __rshift__(self, outra: Callable[[Any], Any]) -> "Fn":
        return Fn(lambda *a, **k: outra(self._f(*a, **k)))

    def __lshift__(self, outra: Callable[..., Any]) -> "Fn":
        return Fn(lambda *a, **k: self._f(outra(*a, **k)))

    def __rrshift__(self, valor: Any) -> Any:
        """valor >> fn aplica a função ao valor."""
        return self._f(valor)

    def __or__(self, outra: Callable[[Any], Any]) -> "Fn":
        return self >> outra


def mapa(f: Callable[[Any], Any]) -> Callable[[Iterable[Any]], list]:
    return lambda xs: [f(x) for x in xs]


def filtro(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], list]:
    return lambda xs: [x for x in xs if pred(x)]


def reduzir(f: Callable[[Any, Any], Any], inicial: Any) -> Callable[[Iterable[Any]], Any]:
    return lambda xs: reduce(f, xs, inicial)


def espiar(efeito: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """tap: executa efeito colateral e devolve o valor intacto."""
    def f(x: Any) -> Any:
        efeito(x)
        return x
    return f


def atributo(nome: str) -> Callable[[Any], Any]:
    return lambda obj: getattr(obj, nome)


def metodo(nome: str, *args: Any, **kwargs: Any) -> Callable[[Any], Any]:
    return lambda obj: getattr(obj, nome)(*args, **kwargs)


def contar_palavras_unicas(texto: str) -> int:
    """Exemplo point-free."""
    return pipe(str.lower, str.split, set, len)(texto)
