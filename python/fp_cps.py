"""Continuation-passing style, mônada Cont e call/cc simulado."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Tuple


# --- Funções em CPS puro ------------------------------------------------------------

def fatorial_cps(n: int, k: Callable[[int], Any]) -> Any:
    if n < 0:
        raise ValueError("n deve ser >= 0")
    if n <= 1:
        return k(1)
    return fatorial_cps(n - 1, lambda r: k(n * r))


def fibonacci_cps(n: int, k: Callable[[int], Any]) -> Any:
    if n < 2:
        return k(n)
    return fibonacci_cps(n - 1, lambda a: fibonacci_cps(n - 2, lambda b: k(a + b)))


def mapear_cps(f: Callable[[Any, Callable], Any], itens: List[Any], k: Callable[[List[Any]], Any]) -> Any:
    if not itens:
        return k([])
    return f(itens[0], lambda y: mapear_cps(f, itens[1:], lambda ys: k([y] + ys)))


def soma_arvore_cps(arvore: Optional[Tuple[Any, Any, Any]], k: Callable[[int], Any]) -> Any:
    """Árvore como (esq, valor, dir) ou None."""
    if arvore is None:
        return k(0)
    esq, valor, dir_ = arvore
    return soma_arvore_cps(esq, lambda se: soma_arvore_cps(dir_, lambda sd: k(se + valor + sd)))


def produto_com_saida(itens: Iterable[int], saida: Callable[[int], Any], k: Callable[[int], Any]) -> Any:
    """Multiplica; ao achar 0 chama `saida` descartando a continuação normal."""
    acc = 1
    for x in itens:
        if x == 0:
            return saida(0)
        acc *= x
    return k(acc)


# --- Mônada de continuação ---------------------------------------------------------------

@dataclass(frozen=True)
class Cont:
    """Cont r a = (a -> r) -> r."""
    rodar: Callable[[Callable[[Any], Any]], Any]

    def executar(self, k: Callable[[Any], Any] = lambda x: x) -> Any:
        return self.rodar(k)

    def map(self, f: Callable[[Any], Any]) -> "Cont":
        return Cont(lambda k: self.rodar(lambda a: k(f(a))))

    def bind(self, f: Callable[[Any], "Cont"]) -> "Cont":
        return Cont(lambda k: self.rodar(lambda a: f(a).rodar(k)))

    def ap(self, outro: "Cont") -> "Cont":
        return self.bind(lambda f: outro.map(f))


def unit(valor: Any) -> Cont:
    return Cont(lambda k: k(valor))


def call_cc(f: Callable[[Callable[[Any], Cont]], Cont]) -> Cont:
    """f recebe `escapar`; chamar escapar(a) abandona o resto e entrega a à continuação capturada."""
    def rodar(k: Callable[[Any], Any]) -> Any:
        escapar = lambda a: Cont(lambda _descartada: k(a))
        return f(escapar).rodar(k)
    return Cont(rodar)


def produto(itens: Iterable[int]) -> Cont:
    """Produto com saída antecipada via call/cc quando aparece um zero."""
    def corpo(escapar: Callable[[Any], Cont]) -> Cont:
        acc = unit(1)
        for x in itens:
            if x == 0:
                return escapar(0)
            acc = acc.map(lambda a, x=x: a * x)
        return acc
    return call_cc(corpo)


def procurar(pred: Callable[[Any], bool], itens: Iterable[Any]) -> Cont:
    """Primeiro elemento que satisfaz pred (ou None), retornando cedo."""
    def corpo(escapar: Callable[[Any], Cont]) -> Cont:
        for x in itens:
            if pred(x):
                return escapar(x)
        return unit(None)
    return call_cc(corpo)


def tentar_cc(corpo: Callable[[Callable[[Any], Cont]], Cont],
              tratador: Callable[[Any], Cont]) -> Cont:
    """Exceções como continuações: lancar(e) desvia para o tratador."""
    marca = object()
    return call_cc(
        lambda lancar_cc: corpo(lambda e: lancar_cc((marca, e)))
    ).bind(
        lambda r: tratador(r[1]) if isinstance(r, tuple) and r and r[0] is marca else unit(r)
    )
