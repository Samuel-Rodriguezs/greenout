"""Verificador de tipos simples para Mini (int, bool, void).

Regras: aritmética só com int; ``< <= > >=`` comparam int e dão bool;
``== !=`` exigem operandos do mesmo tipo; ``&& || !`` exigem bool; condições
de ``if``/``while`` são bool; atribuições, argumentos e ``return`` respeitam
o tipo declarado; função não-void precisa retornar em todos os caminhos.

Nomes não resolvidos são tratados como "desconhecido" (``None``), compatível
com tudo, para não duplicar erros que comp_semantica já reporta.
"""
from __future__ import annotations

from typing import Optional

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_lexer import ErroMini

ARITMETICOS = {"+", "-", "*", "/", "%"}
RELACIONAIS = {"<", "<=", ">", ">="}
IGUALDADE = {"==", "!="}
LOGICOS = {"&&", "||"}


class ErroTipo(ErroMini):
    pass


def sempre_retorna(stmts: list[No]) -> bool:
    """True se toda execução desta sequência termina em ``return``."""
    for s in stmts:
        if isinstance(s, Retorno):
            return True
        if isinstance(s, Bloco) and sempre_retorna(s.stmts):
            return True
        if isinstance(s, Se) and s.senao is not None \
                and sempre_retorna(s.entao.stmts) and sempre_retorna(s.senao.stmts):
            return True
    return False


class _Verificador:
    def __init__(self, programa: Programa) -> None:
        self.erros: list[ErroTipo] = []
        self.funcs: dict[str, tuple[list[str], str]] = {
            f.nome: ([p.tipo for p in f.params], f.ret) for f in programa.funcoes()}
        self.escopos: list[dict[str, Optional[str]]] = []
        self.ret_atual: Optional[str] = None
        self.em_funcao = False

    def erro(self, msg: str, no: No, tamanho: int = 1) -> None:
        self.erros.append(ErroTipo(msg, no.pos[0], no.pos[1], tamanho))

    def buscar(self, nome: str) -> tuple[bool, Optional[str]]:
        for esc in reversed(self.escopos):
            if nome in esc:
                return True, esc[nome]
        return False, None

    # --- programa ---------------------------------------------------------
    def programa(self, p: Programa) -> None:
        for f in p.funcoes():
            self.funcao(f)
        self.escopos = [{}]
        self.em_funcao = False
        for item in p.itens:
            if not isinstance(item, Funcao):
                self.stmt(item)

    def funcao(self, f: Funcao) -> None:
        self.escopos = [{p.nome: p.tipo for p in f.params}, {}]
        self.ret_atual = f.ret
        self.em_funcao = True
        for s in f.corpo.stmts:
            self.stmt(s)
        if f.ret != "void" and not sempre_retorna(f.corpo.stmts):
            self.erro(f"função '{f.nome}' pode terminar sem retornar {f.ret}",
                      f, len(f.nome))

    # --- comandos ---------------------------------------------------------
    def bloco(self, b: Bloco) -> None:
        self.escopos.append({})
        for s in b.stmts:
            self.stmt(s)
        self.escopos.pop()

    def valor(self, e: No) -> Optional[str]:
        """Tipo de uma expressão usada como valor (void é erro)."""
        t = self.expr(e)
        if t == "void":
            self.erro("expressão sem valor (função void)", e)
            return None
        return t

    def condicao(self, e: No, quem: str) -> None:
        t = self.valor(e)
        if t is not None and t != "bool":
            self.erro(f"condição do '{quem}' deve ser bool, não {t}", e)

    def stmt(self, s: No) -> None:
        if isinstance(s, Var):
            t = self.valor(s.init)
            if s.tipo is not None and t is not None and t != s.tipo:
                self.erro(f"'{s.nome}' declarado {s.tipo} mas inicializado com {t}",
                          s.init)
            self.escopos[-1][s.nome] = s.tipo or t
        elif isinstance(s, Atrib):
            existe, alvo = self.buscar(s.nome)
            t = self.valor(s.valor)
            if existe and alvo is not None and t is not None and alvo != t:
                self.erro(f"atribuição de {t} a '{s.nome}' do tipo {alvo}", s.valor)
        elif isinstance(s, Se):
            self.condicao(s.cond, "if")
            self.bloco(s.entao)
            if s.senao is not None:
                self.bloco(s.senao)
        elif isinstance(s, Enquanto):
            self.condicao(s.cond, "while")
            self.bloco(s.corpo)
        elif isinstance(s, Retorno):
            if not self.em_funcao:
                return
            if s.valor is None:
                if self.ret_atual != "void":
                    self.erro(f"return sem valor em função {self.ret_atual}", s, 6)
            else:
                t = self.valor(s.valor)
                if self.ret_atual == "void":
                    self.erro("return com valor em função void", s.valor)
                elif t is not None and t != self.ret_atual:
                    self.erro(f"return de {t} em função {self.ret_atual}", s.valor)
        elif isinstance(s, Imprimir):
            self.valor(s.valor)
        elif isinstance(s, ExprStmt):
            self.expr(s.expr)
        elif isinstance(s, Bloco):
            self.bloco(s)

    # --- expressões -------------------------------------------------------
    def expr(self, e: No) -> Optional[str]:
        if isinstance(e, Num):
            return "int"
        if isinstance(e, Bool):
            return "bool"
        if isinstance(e, Nome):
            return self.buscar(e.nome)[1]
        if isinstance(e, Unario):
            t = self.valor(e.operando)
            esperado = "int" if e.op == "-" else "bool"
            if t is not None and t != esperado:
                self.erro(f"operador '{e.op}' exige {esperado}, recebeu {t}", e)
            return esperado
        if isinstance(e, Binario):
            return self.binario(e)
        if isinstance(e, Chamada):
            sig = self.funcs.get(e.nome)
            tipos = [self.valor(a) for a in e.args]
            if sig is None:
                return None
            params, ret = sig
            if len(params) == len(tipos):
                for i, (esp, t, a) in enumerate(zip(params, tipos, e.args), 1):
                    if t is not None and t != esp:
                        self.erro(f"argumento {i} de '{e.nome}': esperado {esp}, "
                                  f"recebeu {t}", a)
            return ret
        return None

    def binario(self, e: Binario) -> Optional[str]:
        a, b = self.valor(e.esq), self.valor(e.dir)
        if e.op in ARITMETICOS or e.op in RELACIONAIS:
            for t in (a, b):
                if t is not None and t != "int":
                    self.erro(f"operador '{e.op}' exige int, recebeu {t}", e)
                    break
            return "int" if e.op in ARITMETICOS else "bool"
        if e.op in LOGICOS:
            for t in (a, b):
                if t is not None and t != "bool":
                    self.erro(f"operador '{e.op}' exige bool, recebeu {t}", e)
                    break
            return "bool"
        if a is not None and b is not None and a != b:
            self.erro(f"comparação '{e.op}' entre {a} e {b}", e)
        return "bool"


def verificar(programa: Programa) -> list[ErroTipo]:
    v = _Verificador(programa)
    v.programa(programa)
    return v.erros


def tipo_da_expressao(fonte_expr: No, programa: Optional[Programa] = None,
                      variaveis: Optional[dict[str, str]] = None) -> Optional[str]:
    """Tipo de uma expressão avulsa (útil para REPL e testes)."""
    v = _Verificador(programa or Programa([]))
    v.escopos = [dict(variaveis or {})]
    return v.expr(fonte_expr)
