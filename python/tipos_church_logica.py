"""Booleanos e pares de Church, com conversão de/para valores Python."""
from __future__ import annotations

from tipos_beta import normalizar
from tipos_termos import App, Termo, Var, alfa_equivalentes, analisar

VERDADEIRO = analisar("\\t f.t")
FALSO = analisar("\\t f.f")
SE = analisar("\\b t e.b t e")
NAO = analisar("\\b.b (\\t f.f) (\\t f.t)")
E = analisar("\\a b.a b (\\t f.f)")
OU = analisar("\\a b.a (\\t f.t) b")
XOU = analisar("\\a b.a (b (\\t f.f) (\\t f.t)) b")

PAR = analisar("\\a b s.s a b")
PRIMEIRO = analisar("\\p.p (\\a b.a)")
SEGUNDO = analisar("\\p.p (\\a b.b)")


def aplicar(f: Termo, *args: Termo) -> Termo:
    for a in args:
        f = App(f, a)
    return f


def de_bool(b: bool) -> Termo:
    return VERDADEIRO if b else FALSO


def para_bool(t: Termo) -> bool:
    """Observa um booleano de Church aplicando-o a dois marcadores livres."""
    r = normalizar(aplicar(t, Var("#V"), Var("#F")))
    if r == Var("#V"):
        return True
    if r == Var("#F"):
        return False
    raise ValueError("não é um booleano de Church")


def par(a: Termo, b: Termo) -> Termo:
    return aplicar(PAR, a, b)


def primeiro(p: Termo) -> Termo:
    return normalizar(App(PRIMEIRO, p))


def segundo(p: Termo) -> Termo:
    return normalizar(App(SEGUNDO, p))


def igual_a(a: Termo, b: Termo) -> bool:
    return alfa_equivalentes(normalizar(a), normalizar(b))
