"""Recursão com trampolim (sem estourar a pilha) e memoização."""
from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple


@dataclass(frozen=True)
class Pronto:
    valor: Any


@dataclass(frozen=True)
class Chamada:
    """Passo pendente: chamar f(*args) mais tarde."""
    f: Callable[..., Any]
    args: Tuple[Any, ...]


def chamar(f: Callable[..., Any], *args: Any) -> Chamada:
    return Chamada(f, args)


def retornar(valor: Any) -> Pronto:
    return Pronto(valor)


def executar(resultado: Any) -> Any:
    """Roda o laço do trampolim até obter um Pronto (ou valor comum)."""
    while isinstance(resultado, Chamada):
        resultado = resultado.f(*resultado.args)
    if isinstance(resultado, Pronto):
        return resultado.valor
    return resultado


def trampolim(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador: a função devolve Pronto/Chamada e a chamada externa executa o laço."""
    @functools.wraps(f)
    def envolvida(*args: Any, **kwargs: Any) -> Any:
        return executar(f(*args, **kwargs))
    envolvida.passo = f  # type: ignore[attr-defined]
    return envolvida


# Exemplos -------------------------------------------------------------------

@trampolim
def soma_ate(n: int, acc: int = 0) -> Any:
    """Soma 1..n em recursão de cauda via trampolim."""
    if n == 0:
        return Pronto(acc)
    return Chamada(soma_ate.passo, (n - 1, acc + n))


def _par(n: int) -> Any:
    return Pronto(True) if n == 0 else Chamada(_impar, (n - 1,))


def _impar(n: int) -> Any:
    return Pronto(False) if n == 0 else Chamada(_par, (n - 1,))


def eh_par(n: int) -> bool:
    """Recursão mútua com 10^6 de profundidade sem RecursionError."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    return executar(_par(n))


def _fat(n: int, acc: int) -> Any:
    return Pronto(acc) if n <= 1 else Chamada(_fat, (n - 1, acc * n))


def fatorial(n: int) -> int:
    if n < 0:
        raise ValueError("n deve ser >= 0")
    return executar(_fat(n, 1))


# Memoização ------------------------------------------------------------------

class Memoizada:
    """Memoiza por argumentos posicionais hasheáveis e conta acertos/erros."""

    def __init__(self, f: Callable[..., Any]):
        self._f = f
        self._cache: Dict[Tuple[Any, ...], Any] = {}
        self.acertos = 0
        self.erros = 0
        functools.update_wrapper(self, f)

    def __call__(self, *args: Any) -> Any:
        if args in self._cache:
            self.acertos += 1
            return self._cache[args]
        self.erros += 1
        valor = self._f(*args)
        self._cache[args] = valor
        return valor

    def limpar(self) -> None:
        self._cache.clear()
        self.acertos = self.erros = 0

    def __len__(self) -> int:
        return len(self._cache)


def memoizar(f: Callable[..., Any]) -> Memoizada:
    return Memoizada(f)


@memoizar
def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n deve ser >= 0")
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)
