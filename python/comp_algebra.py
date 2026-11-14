"""Simplificação algébrica da AST de Mini.

Identidades aplicadas (``x`` é qualquer expressão; as que descartam ``x``
exigem que ele seja puro, isto é, sem chamadas de função)::

    x + 0, 0 + x, x - 0, x * 1, 1 * x, x / 1  ->  x
    0 - x -> -x        x * 0, 0 * x, x % 1 -> 0       x - x -> 0
    x == x, x <= x, x >= x -> true      x != x, x < x, x > x -> false
    x && true, true && x, x || false, false || x, x && x, x || x -> x
    x && false -> false     x || true -> true
    !!x -> x      --x -> x      !(a < b) -> a >= b  (e demais relacionais)
"""
from __future__ import annotations

from comp_ast import Binario, Bool, No, Num, Unario
from comp_visitor import Transformador, eh_pura

NEGACAO_RELACIONAL = {"<": ">=", "<=": ">", ">": "<=", ">=": "<"}


def _eh(no: No, valor: int) -> bool:
    return isinstance(no, Num) and no.valor == valor


def _bool(no: No, valor: bool) -> bool:
    return isinstance(no, Bool) and no.valor is valor


class _Simplificador(Transformador):
    def transformar_Unario(self, no: Unario) -> No:
        op = self.transformar(no.operando)
        if isinstance(op, Unario) and op.op == no.op:
            return op.operando  # !!x e --x
        if no.op == "!" and isinstance(op, Binario) and op.op in NEGACAO_RELACIONAL:
            return Binario(NEGACAO_RELACIONAL[op.op], op.esq, op.dir, pos=op.pos)
        return Unario(no.op, op, pos=no.pos)

    def transformar_Binario(self, no: Binario) -> No:
        e = self.transformar(no.esq)
        d = self.transformar(no.dir)
        r = self._regras(no.op, e, d, no.pos)
        return r if r is not None else Binario(no.op, e, d, pos=no.pos)

    def _regras(self, op: str, e: No, d: No, pos: tuple[int, int]) -> No | None:
        if op == "+":
            if _eh(d, 0):
                return e
            if _eh(e, 0):
                return d
        elif op == "-":
            if _eh(d, 0):
                return e
            if _eh(e, 0):
                return Unario("-", d, pos=pos)
            if e == d and eh_pura(e):
                return Num(0, pos=pos)
        elif op == "*":
            if _eh(d, 1):
                return e
            if _eh(e, 1):
                return d
            if _eh(d, 0) and eh_pura(e) or _eh(e, 0) and eh_pura(d):
                return Num(0, pos=pos)
        elif op == "/":
            if _eh(d, 1):
                return e
        elif op == "%":
            if _eh(d, 1) and eh_pura(e):
                return Num(0, pos=pos)
        elif op in ("==", "<=", ">="):
            if e == d and eh_pura(e):
                return Bool(True, pos=pos)
        elif op in ("!=", "<", ">"):
            if e == d and eh_pura(e):
                return Bool(False, pos=pos)
        elif op == "&&":
            if _bool(d, True):
                return e
            if _bool(e, True):
                return d
            if _bool(d, False) and eh_pura(e):
                return Bool(False, pos=pos)
            if e == d and eh_pura(e):
                return e
        elif op == "||":
            if _bool(d, False):
                return e
            if _bool(e, False):
                return d
            if _bool(d, True) and eh_pura(e):
                return Bool(True, pos=pos)
            if e == d and eh_pura(e):
                return e
        return None


def simplificar(no: No) -> No:
    """Aplica as identidades até não haver mais mudanças."""
    atual = no
    while True:
        novo = _Simplificador().transformar(atual)
        if novo == atual:
            return novo
        atual = novo
