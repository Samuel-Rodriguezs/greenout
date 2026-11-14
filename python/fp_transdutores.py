"""Transducers: transformações componíveis independentes da coleção de origem."""
from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable, Iterable, List

Redutor = Callable[..., Any]


@dataclass(frozen=True)
class Reduzido:
    """Sinaliza parada antecipada da redução."""
    valor: Any


def _reduzido(x: Any) -> bool:
    return isinstance(x, Reduzido)


def mapa(f: Callable[[Any], Any]) -> Callable[[Redutor], Redutor]:
    def xf(rf: Redutor) -> Redutor:
        return lambda acc, x: rf(acc, f(x))
    return xf


def filtro(pred: Callable[[Any], bool]) -> Callable[[Redutor], Redutor]:
    def xf(rf: Redutor) -> Redutor:
        return lambda acc, x: rf(acc, x) if pred(x) else acc
    return xf


def pegar(n: int) -> Callable[[Redutor], Redutor]:
    """Passa só os n primeiros; estado criado a cada aplicação do transdutor."""
    def xf(rf: Redutor) -> Redutor:
        restante = [n]

        def passo(acc, x):
            if restante[0] <= 0:
                return Reduzido(acc)
            restante[0] -= 1
            acc = rf(acc, x)
            if restante[0] <= 0 and not _reduzido(acc):
                return Reduzido(acc)
            return acc
        return passo
    return xf


def largar(n: int) -> Callable[[Redutor], Redutor]:
    def xf(rf: Redutor) -> Redutor:
        restante = [n]

        def passo(acc, x):
            if restante[0] > 0:
                restante[0] -= 1
                return acc
            return rf(acc, x)
        return passo
    return xf


def pegar_enquanto(pred: Callable[[Any], bool]) -> Callable[[Redutor], Redutor]:
    def xf(rf: Redutor) -> Redutor:
        return lambda acc, x: rf(acc, x) if pred(x) else Reduzido(acc)
    return xf


def achatar() -> Callable[[Redutor], Redutor]:
    def xf(rf: Redutor) -> Redutor:
        def passo(acc, xs):
            for x in xs:
                acc = rf(acc, x)
                if _reduzido(acc):
                    return acc
            return acc
        return passo
    return xf


def compor_xf(*xfs: Callable[[Redutor], Redutor]) -> Callable[[Redutor], Redutor]:
    """Compõe transdutores; a ordem de leitura é a ordem de aplicação aos dados."""
    def xf(rf: Redutor) -> Redutor:
        return reduce(lambda r, t: t(r), reversed(xfs), rf)
    return xf


def transduzir(xf: Callable[[Redutor], Redutor], rf: Redutor, inicial: Any,
               itens: Iterable[Any]) -> Any:
    passo = xf(rf)
    acc = inicial
    for x in itens:
        acc = passo(acc, x)
        if _reduzido(acc):
            return acc.valor
    return acc


def _anexar(acc: List[Any], x: Any) -> List[Any]:
    acc.append(x)
    return acc


def para_lista(xf: Callable[[Redutor], Redutor], itens: Iterable[Any]) -> List[Any]:
    return transduzir(xf, _anexar, [], itens)


def somar(xf: Callable[[Redutor], Redutor], itens: Iterable[Any]) -> Any:
    return transduzir(xf, lambda a, x: a + x, 0, itens)
