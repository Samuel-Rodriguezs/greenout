"""Tipos algébricos de dados (dataclasses frozen) e pattern matching estrutural.

Álgebra simbólica: avaliar, derivar, simplificar e imprimir expressões.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Union


@dataclass(frozen=True)
class Num:
    valor: float


@dataclass(frozen=True)
class Var:
    nome: str


@dataclass(frozen=True)
class Soma:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Mul:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Pot:
    base: "Expr"
    exp: int


Expr = Union[Num, Var, Soma, Mul, Pot]


def avaliar(e: Expr, ambiente: Dict[str, float]) -> float:
    match e:
        case Num(v):
            return v
        case Var(nome):
            if nome not in ambiente:
                raise KeyError(f"variável livre: {nome}")
            return ambiente[nome]
        case Soma(a, b):
            return avaliar(a, ambiente) + avaliar(b, ambiente)
        case Mul(a, b):
            return avaliar(a, ambiente) * avaliar(b, ambiente)
        case Pot(base, n):
            return avaliar(base, ambiente) ** n
    raise TypeError(f"expressão inválida: {e!r}")


def derivar(e: Expr, x: str) -> Expr:
    match e:
        case Num(_):
            return Num(0)
        case Var(nome):
            return Num(1 if nome == x else 0)
        case Soma(a, b):
            return Soma(derivar(a, x), derivar(b, x))
        case Mul(a, b):
            return Soma(Mul(derivar(a, x), b), Mul(a, derivar(b, x)))
        case Pot(base, n):
            return Mul(Mul(Num(n), Pot(base, n - 1)), derivar(base, x))
    raise TypeError(f"expressão inválida: {e!r}")


def _simplifica_no(e: Expr) -> Expr:
    match e:
        case Soma(Num(0), x) | Soma(x, Num(0)):
            return x
        case Soma(Num(a), Num(b)):
            return Num(a + b)
        case Mul(Num(0), _) | Mul(_, Num(0)):
            return Num(0)
        case Mul(Num(1), x) | Mul(x, Num(1)):
            return x
        case Mul(Num(a), Num(b)):
            return Num(a * b)
        case Pot(_, 0):
            return Num(1)
        case Pot(x, 1):
            return x
        case Pot(Num(a), n):
            return Num(a ** n)
    return e


def simplificar(e: Expr) -> Expr:
    """Simplifica de baixo para cima até o ponto fixo."""
    while True:
        match e:
            case Soma(a, b):
                novo = _simplifica_no(Soma(simplificar(a), simplificar(b)))
            case Mul(a, b):
                novo = _simplifica_no(Mul(simplificar(a), simplificar(b)))
            case Pot(base, n):
                novo = _simplifica_no(Pot(simplificar(base), n))
            case _:
                novo = e
        if novo == e:
            return e
        e = novo


def _fmt_num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else str(v)


def mostrar(e: Expr, prec: int = 0) -> str:
    match e:
        case Num(v):
            return _fmt_num(v)
        case Var(nome):
            return nome
        case Soma(a, b):
            s = f"{mostrar(a, 1)} + {mostrar(b, 1)}"
            return f"({s})" if prec > 1 else s
        case Mul(a, b):
            s = f"{mostrar(a, 2)} * {mostrar(b, 2)}"
            return f"({s})" if prec > 2 else s
        case Pot(base, n):
            return f"{mostrar(base, 4)}^{n}"
    raise TypeError(f"expressão inválida: {e!r}")


def variaveis(e: Expr) -> frozenset:
    match e:
        case Num(_):
            return frozenset()
        case Var(nome):
            return frozenset({nome})
        case Soma(a, b) | Mul(a, b):
            return variaveis(a) | variaveis(b)
        case Pot(base, _):
            return variaveis(base)
    raise TypeError(f"expressão inválida: {e!r}")


def classificar(valor: Any) -> str:
    """Demonstra padrões de sequência, mapeamento, classe, guardas e OR."""
    match valor:
        case None:
            return "nada"
        case bool():
            return "booleano"
        case int(n) if n < 0:
            return "inteiro negativo"
        case 0 | 0.0:
            return "zero"
        case int() | float():
            return "número positivo"
        case str() as s if not s:
            return "texto vazio"
        case str():
            return "texto"
        case []:
            return "sequência vazia"
        case [x]:
            return f"unitária de {classificar(x)}"
        case [primeiro, *_, ultimo]:
            return f"sequência de {primeiro!r} a {ultimo!r}"
        case {"tipo": tipo, **resto}:
            return f"registro {tipo} com {len(resto)} campos"
        case dict():
            return "mapa"
        case Num() | Var():
            return "átomo"
        case _:
            return "desconhecido"
