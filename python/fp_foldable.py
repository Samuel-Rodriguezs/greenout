"""Foldable e Traversable para uma árvore binária imutável."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterator, Tuple, Union


@dataclass(frozen=True)
class Folha:
    pass


@dataclass(frozen=True)
class No:
    esq: "Arvore"
    valor: Any
    dir: "Arvore"


Arvore = Union[Folha, No]
VAZIA = Folha()


def de_iteravel(itens) -> Arvore:
    """Constrói uma árvore balanceada preservando a ordem em-ordem."""
    xs = list(itens)

    def build(lo: int, hi: int) -> Arvore:
        if lo >= hi:
            return VAZIA
        m = (lo + hi) // 2
        return No(build(lo, m), xs[m], build(m + 1, hi))
    return build(0, len(xs))


def fmap(f: Callable[[Any], Any], t: Arvore) -> Arvore:
    if isinstance(t, Folha):
        return t
    return No(fmap(f, t.esq), f(t.valor), fmap(f, t.dir))


def dobrar_d(f: Callable[[Any, Any], Any], inicial: Any, t: Arvore) -> Any:
    """foldr em ordem: f(valor, acumulado_da_direita)."""
    if isinstance(t, Folha):
        return inicial
    return dobrar_d(f, f(t.valor, dobrar_d(f, inicial, t.dir)), t.esq)


def dobrar_e(f: Callable[[Any, Any], Any], inicial: Any, t: Arvore) -> Any:
    """foldl em ordem: f(acumulado, valor)."""
    if isinstance(t, Folha):
        return inicial
    return dobrar_e(f, f(dobrar_e(f, inicial, t.esq), t.valor), t.dir)


@dataclass(frozen=True)
class Monoide:
    vazio: Any
    combinar: Callable[[Any, Any], Any]


SOMA = Monoide(0, lambda a, b: a + b)
PRODUTO = Monoide(1, lambda a, b: a * b)
TODOS = Monoide(True, lambda a, b: a and b)
ALGUM = Monoide(False, lambda a, b: a or b)
LISTA = Monoide((), lambda a, b: a + b)


def fold_map(m: Monoide, f: Callable[[Any], Any], t: Arvore) -> Any:
    return dobrar_d(lambda x, acc: m.combinar(f(x), acc), m.vazio, t)


def para_lista(t: Arvore) -> list:
    return list(dobrar_d(lambda x, acc: (x,) + acc, (), t))


def tamanho(t: Arvore) -> int:
    return fold_map(SOMA, lambda _: 1, t)


def elem(x: Any, t: Arvore) -> bool:
    return fold_map(ALGUM, lambda v: v == x, t)


def altura(t: Arvore) -> int:
    if isinstance(t, Folha):
        return 0
    return 1 + max(altura(t.esq), altura(t.dir))


def percorrer(t: Arvore) -> Iterator[Any]:
    if isinstance(t, No):
        yield from percorrer(t.esq)
        yield t.valor
        yield from percorrer(t.dir)


# Traversable ---------------------------------------------------------------

def traverse(f: Callable[[Any], Any], t: Arvore,
             pure: Callable[[Any], Any],
             lift2: Callable[[Callable, Any, Any], Any]) -> Any:
    """Percorre t aplicando f (a -> F b) e combinando efeitos em ordem.

    `pure` e `lift2(f, fa, fb)` definem o Applicative F utilizado.
    """
    if isinstance(t, Folha):
        return pure(VAZIA)
    esq = traverse(f, t.esq, pure, lift2)
    meio = f(t.valor)
    dir_ = traverse(f, t.dir, pure, lift2)
    pares = lift2(lambda e, m: (e, m), esq, meio)
    return lift2(lambda p, d: No(p[0], p[1], d), pares, dir_)


def sequence(t: Arvore, pure, lift2) -> Any:
    return traverse(lambda x: x, t, pure, lift2)
