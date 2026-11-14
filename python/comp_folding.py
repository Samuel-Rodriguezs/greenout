"""Constant folding sobre a AST de Mini e semântica dos operadores.

``aplicar_binario``/``aplicar_unario`` definem a semântica de referência dos
operadores, reutilizada pela VM, pelo interpretador de TAC e pelo
transpilador: inteiros ilimitados, ``/`` trunca em direção a zero e ``%``
tem o sinal do dividendo (como em C), de modo que ``a == (a/b)*b + a%b``.

O dobramento nunca elimina uma divisão por zero (o erro continua em tempo de
execução) e respeita curto-circuito: ``false && f()`` vira ``false``, mas
``f() && false`` mantém a chamada.
"""
from __future__ import annotations

from typing import Optional, Union

from comp_ast import Binario, Bool, No, Num, Programa, Unario
from comp_visitor import Transformador

Valor = Union[int, bool]


def dividir(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("divisão por zero")
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def resto(a: int, b: int) -> int:
    return a - b * dividir(a, b)


def aplicar_binario(op: str, a: Valor, b: Valor) -> Valor:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return dividir(a, b)
    if op == "%":
        return resto(a, b)
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "&&":
        return bool(a and b)
    if op == "||":
        return bool(a or b)
    raise ValueError(f"operador binário desconhecido: {op}")


def aplicar_unario(op: str, a: Valor) -> Valor:
    if op == "-":
        return -a
    if op == "!":
        return not a
    raise ValueError(f"operador unário desconhecido: {op}")


def eh_constante(no: No) -> bool:
    return isinstance(no, (Num, Bool))


def valor_de(no: No) -> Optional[Valor]:
    """Valor Python de um literal, ou None se o nó não for literal."""
    if isinstance(no, (Num, Bool)):
        return no.valor
    return None


def literal(v: Valor, pos: tuple[int, int] = (0, 0)) -> No:
    return Bool(v, pos=pos) if isinstance(v, bool) else Num(v, pos=pos)


class _Dobrador(Transformador):
    def transformar_Unario(self, no: Unario) -> No:
        op = self.transformar(no.operando)
        if eh_constante(op):
            return literal(aplicar_unario(no.op, op.valor), no.pos)
        return Unario(no.op, op, pos=no.pos)

    def transformar_Binario(self, no: Binario) -> No:
        esq = self.transformar(no.esq)
        dir_ = self.transformar(no.dir)
        if no.op in ("&&", "||") and isinstance(esq, Bool):
            # curto-circuito: só avalia o lado direito se necessário
            if (no.op == "&&") == esq.valor:
                return dir_
            return Bool(esq.valor, pos=no.pos)
        if eh_constante(esq) and eh_constante(dir_):
            try:
                return literal(aplicar_binario(no.op, esq.valor, dir_.valor), no.pos)
            except ZeroDivisionError:
                pass
        return Binario(no.op, esq, dir_, pos=no.pos)


def dobrar_constantes(no: No) -> No:
    """Devolve nova árvore com as subexpressões constantes calculadas."""
    return _Dobrador().transformar(no)
