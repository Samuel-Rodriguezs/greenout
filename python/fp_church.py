"""Codificação de Church: listas, numerais e booleanos só com funções."""
from __future__ import annotations

from typing import Any, Callable, Iterable, List

# --- Listas -------------------------------------------------------------------------
# Uma lista é seu próprio foldr: lista(c, n) aplica c(cabeça, resto_dobrado) e termina em n.


def nil(c: Callable, n: Any) -> Any:
    return n


def cons(cabeca: Any, cauda: Callable) -> Callable:
    return lambda c, n: c(cabeca, cauda(c, n))


def de_lista(itens: Iterable[Any]) -> Callable:
    r: Callable = nil
    for x in reversed(list(itens)):
        r = cons(x, r)
    return r


def para_lista(l: Callable) -> List[Any]:
    return l(lambda h, acc: [h] + acc, [])


def tamanho(l: Callable) -> int:
    return l(lambda _h, acc: acc + 1, 0)


def vazia(l: Callable) -> bool:
    return l(lambda _h, _acc: False, True)


def cabeca(l: Callable) -> Any:
    if vazia(l):
        raise IndexError("lista vazia")
    return l(lambda h, _acc: h, None)  # o foldr devolve o elemento mais à esquerda


def mapa(f: Callable[[Any], Any], l: Callable) -> Callable:
    return lambda c, n: l(lambda h, acc: c(f(h), acc), n)


def filtro(pred: Callable[[Any], bool], l: Callable) -> Callable:
    return lambda c, n: l(lambda h, acc: c(h, acc) if pred(h) else acc, n)


def anexar(a: Callable, b: Callable) -> Callable:
    return lambda c, n: a(c, b(c, n))


def reverter(l: Callable) -> Callable:
    return l(lambda h, acc: anexar(acc, cons(h, nil)), nil)


def dobrar(f: Callable[[Any, Any], Any], inicial: Any, l: Callable) -> Any:
    return l(f, inicial)


def soma(l: Callable) -> Any:
    return l(lambda h, acc: h + acc, 0)


# --- Booleanos ------------------------------------------------------------------------

def verdadeiro(a: Any, b: Any) -> Any:
    return a


def falso(a: Any, b: Any) -> Any:
    return b


def nao(p: Callable) -> Callable:
    return lambda a, b: p(b, a)


def e_(p: Callable, q: Callable) -> Callable:
    return lambda a, b: p(q(a, b), b)


def ou_(p: Callable, q: Callable) -> Callable:
    return lambda a, b: p(a, q(a, b))


def para_bool(p: Callable) -> bool:
    return p(True, False)


def de_bool(b: bool) -> Callable:
    return verdadeiro if b else falso


# --- Numerais -------------------------------------------------------------------------

def zero(f: Callable, x: Any) -> Any:
    return x


def suc(n: Callable) -> Callable:
    return lambda f, x: f(n(f, x))


def de_int(k: int) -> Callable:
    if k < 0:
        raise ValueError("numerais de Church são naturais")
    n: Callable = zero
    for _ in range(k):
        n = suc(n)
    return n


def para_int(n: Callable) -> int:
    return n(lambda x: x + 1, 0)


def soma_n(a: Callable, b: Callable) -> Callable:
    return lambda f, x: a(f, b(f, x))


def mul_n(a: Callable, b: Callable) -> Callable:
    return lambda f, x: a(lambda y: b(f, y), x)


def exp_n(base: Callable, e: Callable) -> Callable:
    """base^e: aplica 'multiplicar por base' e vezes, partindo de 1."""
    return e(lambda acc: mul_n(base, acc), suc(zero))


def eh_zero(n: Callable) -> Callable:
    return n(lambda _x: falso, verdadeiro)


def pred(n: Callable) -> Callable:
    """Predecessor (pred 0 = 0), via pares (anterior, atual)."""
    par = n(lambda p: (p[1], suc(p[1])), (zero, zero))
    return par[0]


def sub_n(a: Callable, b: Callable) -> Callable:
    return b(pred, a)
