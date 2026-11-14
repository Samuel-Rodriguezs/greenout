"""Propagação de constantes sobre a AST de Mini (análise sensível ao fluxo).

Mantém um ambiente ``nome -> valor constante`` ao percorrer o programa:

* ``var``/atribuição de literal registra o valor; qualquer outro valor o apaga;
* ``if``: cada ramo recebe uma cópia do ambiente e, na junção, só ficam as
  variáveis com o mesmo valor nos dois caminhos;
* ``while``: variáveis atribuídas no laço são esquecidas antes da condição
  e do corpo (o valor de uma iteração não vale para a seguinte);
* blocos restauram o que declaram (sombreamento) ao terminar;
* parâmetros são desconhecidos.

Só substitui ``Nome`` por literal; combine com comp_folding e
comp_codigo_morto para colher o ganho.
"""
from __future__ import annotations

from comp_ast import (Atrib, Binario, Bloco, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Programa, Retorno, Se,
                      Unario, Var)
from comp_folding import Valor, eh_constante, literal
from comp_visitor import percorrer

Ambiente = dict[str, Valor]


def _atribuidas(no: No) -> set[str]:
    return {n.nome for n in percorrer(no) if isinstance(n, Atrib)}


class _Propagador:
    def expr(self, e: No, env: Ambiente) -> No:
        if isinstance(e, Nome):
            if e.nome in env:
                return literal(env[e.nome], e.pos)
            return e
        if isinstance(e, Unario):
            return Unario(e.op, self.expr(e.operando, env), pos=e.pos)
        if isinstance(e, Binario):
            return Binario(e.op, self.expr(e.esq, env), self.expr(e.dir, env), pos=e.pos)
        if isinstance(e, Chamada):
            return Chamada(e.nome, [self.expr(a, env) for a in e.args], pos=e.pos)
        return e

    def bloco(self, b: Bloco, env: Ambiente) -> Bloco:
        antes = dict(env)
        declarados = {s.nome for s in b.stmts if isinstance(s, Var)}
        stmts = [self.stmt(s, env) for s in b.stmts]
        for nome in declarados:  # volta ao que valia fora do bloco
            if nome in antes:
                env[nome] = antes[nome]
            else:
                env.pop(nome, None)
        return Bloco(stmts, pos=b.pos)

    def stmt(self, s: No, env: Ambiente) -> No:
        if isinstance(s, Var):
            init = self.expr(s.init, env)
            self._registrar(s.nome, init, env)
            return Var(s.nome, init, s.tipo, pos=s.pos)
        if isinstance(s, Atrib):
            valor = self.expr(s.valor, env)
            self._registrar(s.nome, valor, env)
            return Atrib(s.nome, valor, pos=s.pos)
        if isinstance(s, Imprimir):
            return Imprimir(self.expr(s.valor, env), pos=s.pos)
        if isinstance(s, ExprStmt):
            return ExprStmt(self.expr(s.expr, env), pos=s.pos)
        if isinstance(s, Retorno):
            return Retorno(None if s.valor is None else self.expr(s.valor, env), pos=s.pos)
        if isinstance(s, Bloco):
            return self.bloco(s, env)
        if isinstance(s, Se):
            cond = self.expr(s.cond, env)
            env_a, env_b = dict(env), dict(env)
            entao = self.bloco(s.entao, env_a)
            senao = self.bloco(s.senao, env_b) if s.senao is not None else None
            env.clear()
            env.update({k: v for k, v in env_a.items()
                        if k in env_b and env_b[k] == v and type(env_b[k]) is type(v)})
            return Se(cond, entao, senao, pos=s.pos)
        if isinstance(s, Enquanto):
            for nome in _atribuidas(s):
                env.pop(nome, None)
            cond = self.expr(s.cond, env)
            corpo = self.bloco(s.corpo, dict(env))
            return Enquanto(cond, corpo, pos=s.pos)
        return s

    @staticmethod
    def _registrar(nome: str, valor: No, env: Ambiente) -> None:
        if eh_constante(valor):
            env[nome] = valor.valor
        else:
            env.pop(nome, None)

    def funcao(self, f: Funcao) -> Funcao:
        corpo = self.bloco(f.corpo, {})
        return Funcao(f.nome, f.params, f.ret, corpo, pos=f.pos)

    def programa(self, p: Programa) -> Programa:
        env: Ambiente = {}
        itens: list[No] = []
        for item in p.itens:
            if isinstance(item, Funcao):
                itens.append(self.funcao(item))
            else:
                itens.append(self.stmt(item, env))
        return Programa(itens, pos=p.pos)


def propagar_constantes(programa: Programa) -> Programa:
    return _Propagador().programa(programa)
