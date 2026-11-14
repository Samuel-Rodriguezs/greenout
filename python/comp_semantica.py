"""Análise semântica de Mini: resolução de nomes, redeclaração e aridade.

Regras:
* funções vivem no escopo global e podem ser chamadas antes da declaração;
* o código de nível superior roda em um escopo ``main`` próprio e funções
  não enxergam as variáveis dele (nem as de outras funções);
* ``var`` só vê o próprio nome depois da inicialização (``var x = x;`` falha);
* blocos, ``if`` e ``while`` abrem escopos; sombrear nome externo é permitido,
  redeclarar no mesmo escopo não;
* ``return`` fora de função é erro.

Os erros são acumulados (não para no primeiro). Tipos ficam a cargo de
comp_tipos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_lexer import ErroMini
from comp_simbolos import ErroRedeclaracao, Simbolo, TabelaSimbolos


class ErroSemantico(ErroMini):
    pass


@dataclass
class ResultadoSemantico:
    erros: list[ErroMini] = field(default_factory=list)
    tabela: TabelaSimbolos = field(default_factory=TabelaSimbolos)

    @property
    def ok(self) -> bool:
        return not self.erros


class _Analisador:
    def __init__(self) -> None:
        self.res = ResultadoSemantico()
        self.t = self.res.tabela
        self.em_funcao = False

    def erro(self, msg: str, no: No, tamanho: int = 1) -> None:
        self.res.erros.append(ErroSemantico(msg, no.pos[0], no.pos[1], tamanho))

    def declarar(self, simbolo: Simbolo) -> None:
        try:
            self.t.declarar(simbolo)
        except ErroRedeclaracao as e:
            self.res.erros.append(e)

    # --- programa ---------------------------------------------------------
    def programa(self, p: Programa) -> None:
        for f in p.funcoes():
            self.declarar(Simbolo(f.nome, "func", f.ret, f.pos,
                                  tuple(x.tipo for x in f.params)))
        for f in p.funcoes():
            self.funcao(f)
        self.t.entrar("main")
        for item in p.itens:
            if not isinstance(item, Funcao):
                self.stmt(item)
        self.t.sair()

    def funcao(self, f: Funcao) -> None:
        self.t.entrar(f.nome)
        self.em_funcao = True
        for param in f.params:
            self.declarar(Simbolo(param.nome, "param", param.tipo, param.pos))
        for s in f.corpo.stmts:  # corpo compartilha o escopo dos parâmetros
            self.stmt(s)
        self.em_funcao = False
        self.t.sair()

    # --- comandos ---------------------------------------------------------
    def bloco(self, b: Bloco, nome: str = "bloco") -> None:
        self.t.entrar(nome)
        for s in b.stmts:
            self.stmt(s)
        self.t.sair()

    def stmt(self, s: No) -> None:
        if isinstance(s, Var):
            self.expr(s.init)
            self.declarar(Simbolo(s.nome, "var", s.tipo or "?", s.pos))
        elif isinstance(s, Atrib):
            alvo = self.t.resolver(s.nome)
            if alvo is None:
                self.erro(f"variável '{s.nome}' não declarada", s, len(s.nome))
            elif alvo.categoria == "func":
                self.erro(f"'{s.nome}' é uma função e não pode receber atribuição",
                          s, len(s.nome))
            self.expr(s.valor)
        elif isinstance(s, Se):
            self.expr(s.cond)
            self.bloco(s.entao, "se")
            if s.senao is not None:
                self.bloco(s.senao, "senao")
        elif isinstance(s, Enquanto):
            self.expr(s.cond)
            self.bloco(s.corpo, "enquanto")
        elif isinstance(s, Retorno):
            if not self.em_funcao:
                self.erro("'return' fora de função", s, 6)
            if s.valor is not None:
                self.expr(s.valor)
        elif isinstance(s, Imprimir):
            self.expr(s.valor)
        elif isinstance(s, ExprStmt):
            self.expr(s.expr)
        elif isinstance(s, Bloco):
            self.bloco(s)
        elif isinstance(s, Funcao):
            self.erro("função declarada fora do nível superior", s, len(s.nome))

    # --- expressões -------------------------------------------------------
    def expr(self, e: No) -> None:
        if isinstance(e, (Num, Bool)):
            return
        if isinstance(e, Nome):
            sim = self.t.resolver(e.nome)
            if sim is None:
                self.erro(f"variável '{e.nome}' não declarada", e, len(e.nome))
            elif sim.categoria == "func":
                self.erro(f"'{e.nome}' é uma função, não uma variável", e, len(e.nome))
        elif isinstance(e, Unario):
            self.expr(e.operando)
        elif isinstance(e, Binario):
            self.expr(e.esq)
            self.expr(e.dir)
        elif isinstance(e, Chamada):
            sim = self.t.resolver(e.nome)
            if sim is None:
                self.erro(f"função '{e.nome}' não declarada", e, len(e.nome))
            elif sim.categoria != "func":
                self.erro(f"'{e.nome}' não é uma função", e, len(e.nome))
            elif sim.aridade != len(e.args):
                self.erro(f"função '{e.nome}' espera {sim.aridade} argumento(s), "
                          f"recebeu {len(e.args)}", e, len(e.nome))
            for a in e.args:
                self.expr(a)


def analisar(programa: Programa) -> ResultadoSemantico:
    a = _Analisador()
    a.programa(programa)
    return a.res
