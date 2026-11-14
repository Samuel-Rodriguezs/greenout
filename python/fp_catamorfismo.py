"""Catamorfismo e anamorfismo via ponto fixo de functores (Fix), mais unfold de listas."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Iterator, Optional, Tuple


@dataclass(frozen=True)
class Fix:
    """Ponto fixo de um functor: Fix[F] = F[Fix[F]]."""
    un: Any


def cata(alg: Callable[[Any], Any], t: Fix) -> Any:
    """Dobra a estrutura de baixo para cima com a álgebra `alg`."""
    return alg(t.un.fmap(lambda filho: cata(alg, filho)))


def ana(coalg: Callable[[Any], Any], semente: Any) -> Fix:
    """Desdobra a estrutura a partir de uma semente com a coálgebra `coalg`."""
    return Fix(coalg(semente).fmap(lambda s: ana(coalg, s)))


def hylo(alg: Callable[[Any], Any], coalg: Callable[[Any], Any], semente: Any) -> Any:
    """cata . ana sem materializar a estrutura intermediária."""
    return alg(coalg(semente).fmap(lambda s: hylo(alg, coalg, s)))


# --- Functor de expressões aritméticas ----------------------------------------

@dataclass(frozen=True)
class NumF:
    valor: Any

    def fmap(self, f: Callable) -> "NumF":
        return self


@dataclass(frozen=True)
class SomaF:
    esq: Any
    dir: Any

    def fmap(self, f: Callable) -> "SomaF":
        return SomaF(f(self.esq), f(self.dir))


@dataclass(frozen=True)
class MulF:
    esq: Any
    dir: Any

    def fmap(self, f: Callable) -> "MulF":
        return MulF(f(self.esq), f(self.dir))


@dataclass(frozen=True)
class NegF:
    arg: Any

    def fmap(self, f: Callable) -> "NegF":
        return replace(self, arg=f(self.arg))


def num(v: Any) -> Fix:
    return Fix(NumF(v))


def soma(a: Fix, b: Fix) -> Fix:
    return Fix(SomaF(a, b))


def mul(a: Fix, b: Fix) -> Fix:
    return Fix(MulF(a, b))


def neg(a: Fix) -> Fix:
    return Fix(NegF(a))


def alg_avaliar(f: Any) -> Any:
    match f:
        case NumF(v):
            return v
        case SomaF(a, b):
            return a + b
        case MulF(a, b):
            return a * b
        case NegF(a):
            return -a


def alg_mostrar(f: Any) -> str:
    match f:
        case NumF(v):
            return str(v)
        case SomaF(a, b):
            return f"({a} + {b})"
        case MulF(a, b):
            return f"({a} * {b})"
        case NegF(a):
            return f"-{a}"


def alg_profundidade(f: Any) -> int:
    match f:
        case NumF(_):
            return 1
        case SomaF(a, b) | MulF(a, b):
            return 1 + max(a, b)
        case NegF(a):
            return 1 + a


def coalg_somas(n: int) -> Any:
    """Semente n vira a árvore de somas 1 + 1 + ... (n folhas)."""
    if n <= 1:
        return NumF(1)
    return SomaF(n // 2, n - n // 2)


# --- Functor de listas ----------------------------------------------------------

@dataclass(frozen=True)
class NilF:
    def fmap(self, f: Callable) -> "NilF":
        return self


@dataclass(frozen=True)
class ConsF:
    cabeca: Any
    resto: Any

    def fmap(self, f: Callable) -> "ConsF":
        return ConsF(self.cabeca, f(self.resto))


def alg_para_lista(f: Any) -> list:
    match f:
        case NilF():
            return []
        case ConsF(h, r):
            return [h] + r


def coalg_intervalo(n: int) -> Any:
    """n, n-1, ..., 1."""
    return NilF() if n <= 0 else ConsF(n, n - 1)


def alg_produto(f: Any) -> int:
    match f:
        case NilF():
            return 1
        case ConsF(h, r):
            return h * r


def fatorial(n: int) -> int:
    """Fatorial como hilomorfismo: desdobra n..1 e dobra multiplicando."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    return hylo(alg_produto, coalg_intervalo, n)


# --- Fold/unfold em iteráveis -----------------------------------------------------

def dobrar_d(f: Callable[[Any, Any], Any], inicial: Any, itens: Any) -> Any:
    """foldr: f(x1, f(x2, ... f(xn, inicial)))."""
    acc = inicial
    for x in reversed(list(itens)):
        acc = f(x, acc)
    return acc


def desdobrar(f: Callable[[Any], Optional[Tuple[Any, Any]]], semente: Any) -> Iterator[Any]:
    """unfold: f(s) devolve (valor, próxima_semente) ou None para parar."""
    while True:
        r = f(semente)
        if r is None:
            return
        valor, semente = r
        yield valor
