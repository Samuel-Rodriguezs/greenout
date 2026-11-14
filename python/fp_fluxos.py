"""Streams preguiçosos (cabeça + cauda memoizada), com primos e Fibonacci infinitos."""
from __future__ import annotations

import operator
from typing import Any, Callable, Iterable, Iterator, List, Optional


class Fluxo:
    """Célula de stream: a cauda é um thunk avaliado no máximo uma vez."""

    __slots__ = ("cabeca", "_cauda_fn", "_cauda", "_avaliada")

    def __init__(self, cabeca: Any, cauda_fn: Callable[[], Optional["Fluxo"]]):
        self.cabeca = cabeca
        self._cauda_fn = cauda_fn
        self._cauda: Optional[Fluxo] = None
        self._avaliada = False

    @property
    def cauda(self) -> Optional["Fluxo"]:
        if not self._avaliada:
            self._cauda = self._cauda_fn()
            self._avaliada = True
            self._cauda_fn = None  # libera a closure
        return self._cauda

    @property
    def cauda_avaliada(self) -> bool:
        return self._avaliada

    def __iter__(self) -> Iterator[Any]:
        no: Optional[Fluxo] = self
        while no is not None:
            yield no.cabeca
            no = no.cauda


def de_iteravel(itens: Iterable[Any]) -> Optional[Fluxo]:
    it = iter(itens)

    def proximo() -> Optional[Fluxo]:
        try:
            x = next(it)
        except StopIteration:
            return None
        return Fluxo(x, proximo)
    return proximo()


def iterar(f: Callable[[Any], Any], semente: Any) -> Fluxo:
    return Fluxo(semente, lambda: iterar(f, f(semente)))


def a_partir(n: int) -> Fluxo:
    return iterar(lambda x: x + 1, n)


def mapear(f: Callable[[Any], Any], s: Optional[Fluxo]) -> Optional[Fluxo]:
    if s is None:
        return None
    return Fluxo(f(s.cabeca), lambda: mapear(f, s.cauda))


def filtrar(pred: Callable[[Any], bool], s: Optional[Fluxo]) -> Optional[Fluxo]:
    while s is not None and not pred(s.cabeca):
        s = s.cauda
    if s is None:
        return None
    return Fluxo(s.cabeca, lambda: filtrar(pred, s.cauda))


def zip_com(f: Callable[[Any, Any], Any], a: Optional[Fluxo], b: Optional[Fluxo]) -> Optional[Fluxo]:
    if a is None or b is None:
        return None
    return Fluxo(f(a.cabeca, b.cabeca), lambda: zip_com(f, a.cauda, b.cauda))


def pegar(n: int, s: Optional[Fluxo]) -> List[Any]:
    saida: List[Any] = []
    while s is not None and len(saida) < n:
        saida.append(s.cabeca)
        s = s.cauda if len(saida) < n else None
    return saida


def pegar_enquanto(pred: Callable[[Any], bool], s: Optional[Fluxo]) -> List[Any]:
    saida: List[Any] = []
    while s is not None and pred(s.cabeca):
        saida.append(s.cabeca)
        s = s.cauda
    return saida


def enesimo(n: int, s: Optional[Fluxo]) -> Any:
    for _ in range(n):
        if s is None:
            raise IndexError(n)
        s = s.cauda
    if s is None:
        raise IndexError(n)
    return s.cabeca


NATURAIS = a_partir(0)


def _eh_primo(n: int) -> bool:
    for p in PRIMOS:
        if p * p > n:
            return True
        if n % p == 0:
            return False
    return True


# Autorreferente: _eh_primo consulta os primos já memoizados.
PRIMOS: Fluxo = Fluxo(2, lambda: filtrar(_eh_primo, a_partir(3)))


def _fib() -> Fluxo:
    return Fluxo(0, lambda: Fluxo(1, lambda: zip_com(operator.add, FIBONACCI, FIBONACCI.cauda)))


FIBONACCI: Fluxo = _fib()
