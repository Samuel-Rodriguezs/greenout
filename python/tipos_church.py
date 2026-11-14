"""Numerais de Church como termos lambda: soma, produto, exponenciação,
sucessor, predecessor e teste de zero."""
from __future__ import annotations

from tipos_beta import normalizar
from tipos_termos import Abs, App, Termo, Var, analisar

ZERO = analisar("\\f x.x")
SUC = analisar("\\n f x.f (n f x)")
SOMA = analisar("\\m n f x.m f (n f x)")
MULT = analisar("\\m n f.m (n f)")
EXP = analisar("\\m n f x.n m f x")
PRED = analisar("\\n f x.n (\\g h.h (g f)) (\\u.x) (\\u.u)")
SUB = analisar("\\m n.n (\\n f x.n (\\g h.h (g f)) (\\u.x) (\\u.u)) m")
E_ZERO = analisar("\\n.n (\\u.\\t f.f) (\\t f.t)")


def de_int(n: int) -> Termo:
    if n < 0:
        raise ValueError("numerais de Church são naturais")
    corpo: Termo = Var("x")
    for _ in range(n):
        corpo = App(Var("f"), corpo)
    return Abs("f", Abs("x", corpo))


def para_int(t: Termo) -> int:
    """Normaliza t e lê o resultado como numeral; ValueError se não for um."""
    t = normalizar(t)
    if not (isinstance(t, Abs) and isinstance(t.corpo, Abs)):
        raise ValueError("não é um numeral de Church")
    f, x = t.param, t.corpo.param
    corpo, n = t.corpo.corpo, 0
    while isinstance(corpo, App):
        if corpo.fun != Var(f):
            raise ValueError("não é um numeral de Church")
        corpo, n = corpo.arg, n + 1
    if corpo != Var(x):
        raise ValueError("não é um numeral de Church")
    return n


def aplicar(f: Termo, *args: Termo) -> Termo:
    for a in args:
        f = App(f, a)
    return f


def soma(a: int, b: int) -> int:
    return para_int(aplicar(SOMA, de_int(a), de_int(b)))


def produto(a: int, b: int) -> int:
    return para_int(aplicar(MULT, de_int(a), de_int(b)))


def potencia(a: int, b: int) -> int:
    return para_int(aplicar(EXP, de_int(a), de_int(b)))


def predecessor(a: int) -> int:
    return para_int(aplicar(PRED, de_int(a)))


def subtracao(a: int, b: int) -> int:
    """Subtração truncada em zero."""
    return para_int(aplicar(SUB, de_int(a), de_int(b)))
