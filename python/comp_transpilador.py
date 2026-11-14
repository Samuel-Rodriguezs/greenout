"""Transpilador de Mini para Python (geração de código a partir da AST).

Mapeamento: funções viram ``def f_<nome>``, variáveis ``v_<nome>`` (sombreadas
ganham ``_1``, ``_2``... pois Python não tem escopo de bloco), o código de
nível superior vira ``_principal()``. ``/`` e ``%`` usam helpers com a mesma
semântica da VM (truncamento em direção a zero); ``&&``/``||`` viram
``and``/``or`` (curto-circuito); ``print`` formata ``true``/``false``.
"""
from __future__ import annotations

import sys
from typing import Any

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_vm import ErroExecucao

PREAMBULO = '''\
def _div(a, b):
    if b == 0:
        raise ZeroDivisionError("divisão por zero")
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def _mod(a, b):
    return a - b * _div(a, b)


def _imprimir(v):
    _saida.append("true" if v is True else "false" if v is False else str(v))
'''

OPERADORES_PY = {"&&": "and", "||": "or"}


class _Transpilador:
    def __init__(self) -> None:
        self.linhas: list[str] = []
        self.escopos: list[dict[str, str]] = []
        self.contagem: dict[str, int] = {}

    def declarar(self, nome: str) -> str:
        n = self.contagem.get(nome, 0)
        self.contagem[nome] = n + 1
        py = f"v_{nome}" if n == 0 else f"v_{nome}_{n}"
        self.escopos[-1][nome] = py
        return py

    def resolver(self, nome: str) -> str:
        for esc in reversed(self.escopos):
            if nome in esc:
                return esc[nome]
        raise KeyError(nome)

    def emitir(self, nivel: int, texto: str) -> None:
        self.linhas.append("    " * nivel + texto)

    # --- expressões -------------------------------------------------------
    def expr(self, e: No) -> str:
        if isinstance(e, Bool):
            return "True" if e.valor else "False"
        if isinstance(e, Num):
            return f"({e.valor})" if e.valor < 0 else str(e.valor)
        if isinstance(e, Nome):
            return self.resolver(e.nome)
        if isinstance(e, Unario):
            return f"(not {self.expr(e.operando)})" if e.op == "!" \
                else f"(-{self.expr(e.operando)})"
        if isinstance(e, Binario):
            a, b = self.expr(e.esq), self.expr(e.dir)
            if e.op == "/":
                return f"_div({a}, {b})"
            if e.op == "%":
                return f"_mod({a}, {b})"
            return f"({a} {OPERADORES_PY.get(e.op, e.op)} {b})"
        if isinstance(e, Chamada):
            return f"f_{e.nome}({', '.join(self.expr(a) for a in e.args)})"
        raise TypeError(f"expressão inválida: {type(e).__name__}")

    # --- comandos ---------------------------------------------------------
    def corpo(self, stmts: list[No], nivel: int) -> None:
        inicio = len(self.linhas)
        self.escopos.append({})
        for s in stmts:
            self.stmt(s, nivel)
        self.escopos.pop()
        if len(self.linhas) == inicio:
            self.emitir(nivel, "pass")

    def stmt(self, s: No, nivel: int) -> None:
        if isinstance(s, Var):
            valor = self.expr(s.init)
            self.emitir(nivel, f"{self.declarar(s.nome)} = {valor}")
        elif isinstance(s, Atrib):
            self.emitir(nivel, f"{self.resolver(s.nome)} = {self.expr(s.valor)}")
        elif isinstance(s, Imprimir):
            self.emitir(nivel, f"_imprimir({self.expr(s.valor)})")
        elif isinstance(s, ExprStmt):
            self.emitir(nivel, self.expr(s.expr))
        elif isinstance(s, Retorno):
            self.emitir(nivel, "return 0" if s.valor is None
                        else f"return {self.expr(s.valor)}")
        elif isinstance(s, Bloco):
            self.escopos.append({})
            for x in s.stmts:
                self.stmt(x, nivel)
            self.escopos.pop()
        elif isinstance(s, Se):
            self.emitir(nivel, f"if {self.expr(s.cond)}:")
            self.corpo(s.entao.stmts, nivel + 1)
            if s.senao is not None:
                self.emitir(nivel, "else:")
                self.corpo(s.senao.stmts, nivel + 1)
        elif isinstance(s, Enquanto):
            self.emitir(nivel, f"while {self.expr(s.cond)}:")
            self.corpo(s.corpo.stmts, nivel + 1)
        else:
            raise TypeError(f"comando inválido: {type(s).__name__}")

    def funcao(self, f: Funcao) -> None:
        self.escopos = [{}]
        self.contagem = {}
        params = [self.declarar(p.nome) for p in f.params]
        self.emitir(0, f"def f_{f.nome}({', '.join(params)}):")
        self.corpo(f.corpo.stmts, 1)
        self.emitir(1, "return 0")
        self.emitir(0, "")
        self.emitir(0, "")

    def principal(self, comandos: list[No]) -> None:
        self.escopos = [{}]
        self.contagem = {}
        self.emitir(0, "def _principal():")
        self.corpo(comandos, 1)
        self.emitir(0, "")
        self.emitir(0, "")


def transpilar(programa: Programa, com_preambulo: bool = True) -> str:
    """Gera o código Python equivalente ao programa Mini."""
    t = _Transpilador()
    for f in programa.funcoes():
        t.funcao(f)
    t.principal(programa.comandos())
    corpo = "\n".join(t.linhas)
    return (PREAMBULO + "\n\n" if com_preambulo else "") + corpo


def executar_python(programa: Programa, limite_recursao: int = 3000) -> list[str]:
    """Transpila, executa com ``exec`` e devolve as linhas impressas."""
    codigo = transpilar(programa) + "_principal()\n"
    saida: list[str] = []
    ns: dict[str, Any] = {"_saida": saida}
    antigo = sys.getrecursionlimit()
    sys.setrecursionlimit(max(antigo, limite_recursao))
    try:
        exec(compile(codigo, "<mini>", "exec"), ns)
    except ZeroDivisionError:
        raise ErroExecucao("divisão por zero") from None
    except RecursionError:
        raise ErroExecucao("estouro da pilha de chamadas") from None
    finally:
        sys.setrecursionlimit(antigo)
    return saida
