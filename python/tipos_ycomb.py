"""Combinadores de ponto fixo Y e Z: como termos lambda e em Python estrito."""
from __future__ import annotations

from typing import Callable, TypeVar

from tipos_beta import normalizar
from tipos_church import E_ZERO, MULT, PRED, de_int, para_int
from tipos_church_logica import SE
from tipos_termos import App, Termo, analisar, substituir

A = TypeVar("A")
B = TypeVar("B")

Y = analisar("\\f.(\\x.f (x x)) (\\x.f (x x))")
Z = analisar("\\f.(\\x.f (\\v.x x v)) (\\x.f (\\v.x x v))")


def fechar(t: Termo, ambiente: dict[str, Termo]) -> Termo:
    """Substitui nomes livres de t pelas definições do ambiente."""
    for nome, def_ in ambiente.items():
        t = substituir(t, nome, def_)
    return t


# Gerador do fatorial: ponto fixo dele é n |-> se n==0 então 1 senão n * f (n-1).
FAT_GERADOR = fechar(
    analisar("\\f n.se (ehzero n) um (mult n (f (pred n)))"),
    {"se": SE, "ehzero": E_ZERO, "um": de_int(1), "mult": MULT, "pred": PRED},
)


def ponto_fixo(combinador: Termo, gerador: Termo) -> Termo:
    return App(combinador, gerador)


def fatorial_church(n: int, combinador: Termo = Y) -> int:
    """Fatorial calculado só com termos lambda (ordem normal)."""
    return para_int(normalizar(App(ponto_fixo(combinador, FAT_GERADOR), de_int(n))))


def z_python(gerador: Callable[[Callable[[A], B]], Callable[[A], B]]) -> Callable[[A], B]:
    """Z em Python: a eta-expansão `lambda v: x(x)(v)` adia a autoaplicação,
    evitando o laço infinito que o Y puro causaria em avaliação estrita."""
    return (lambda x: gerador(lambda v: x(x)(v)))(lambda x: gerador(lambda v: x(x)(v)))


def y_python_estrito(gerador: Callable) -> Callable:
    """Y puro: diverge (RecursionError) em Python por avaliar x(x) antes."""
    return (lambda x: gerador(x(x)))(lambda x: gerador(x(x)))
