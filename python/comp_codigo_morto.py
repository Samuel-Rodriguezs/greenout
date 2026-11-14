"""Eliminação de código morto na AST de Mini.

Remove, repetindo até estabilizar:
* comandos depois de ``return`` (ou de um ``if`` que retorna nos dois ramos);
* ``if`` com condição literal (fica só o ramo vivo) e ``while (false)``;
* comandos de expressão puros e ``if`` vazios;
* variáveis nunca lidas: ``var``/atribuição com valor puro somem; com valor
  impuro sobra só a expressão (para manter os efeitos);
* funções inalcançáveis a partir do código de nível superior;
* blocos sem declarações são achatados no bloco pai.
"""
from __future__ import annotations

from comp_ast import (Atrib, Bloco, Bool, Chamada, Enquanto, ExprStmt, Funcao,
                      No, Nome, Programa, Se, Var)
from comp_tipos import sempre_retorna
from comp_visitor import Transformador, eh_pura, percorrer


class _Limpador(Transformador):
    def lista(self, stmts: list[No]) -> list[No]:
        saida: list[No] = []
        for s in stmts:
            r = self.transformar(s)
            itens = [] if r is None else (r if isinstance(r, list) else [r])
            for it in itens:
                if isinstance(it, Bloco) and not any(isinstance(x, Var) for x in it.stmts):
                    saida.extend(it.stmts)
                else:
                    saida.append(it)
            if saida and sempre_retorna([saida[-1]]):
                break
        return saida

    def transformar_Bloco(self, no: Bloco) -> Bloco:
        return Bloco(self.lista(no.stmts), pos=no.pos)

    def transformar_Programa(self, no: Programa) -> Programa:
        return Programa(self.lista(no.itens), pos=no.pos)

    def transformar_ExprStmt(self, no: ExprStmt) -> No | None:
        expr = self.transformar(no.expr)
        return None if eh_pura(expr) else ExprStmt(expr, pos=no.pos)

    def transformar_Se(self, no: Se) -> No | None:
        cond = self.transformar(no.cond)
        entao = self.transformar(no.entao)
        senao = self.transformar(no.senao) if no.senao is not None else None
        if isinstance(cond, Bool):
            return entao if cond.valor else senao
        if not entao.stmts and (senao is None or not senao.stmts):
            return None if eh_pura(cond) else ExprStmt(cond, pos=no.pos)
        if senao is not None and not senao.stmts:
            senao = None
        return Se(cond, entao, senao, pos=no.pos)

    def transformar_Enquanto(self, no: Enquanto) -> No | None:
        cond = self.transformar(no.cond)
        if isinstance(cond, Bool) and not cond.valor:
            return None
        return Enquanto(cond, self.transformar(no.corpo), pos=no.pos)


class _SemUso(Transformador):
    def __init__(self, lidas: set[str]) -> None:
        self.lidas = lidas

    def _descartar(self, valor: No, pos: tuple[int, int]) -> No | None:
        return None if eh_pura(valor) else ExprStmt(valor, pos=pos)

    def transformar_Var(self, no: Var) -> No | None:
        if no.nome in self.lidas:
            return self.generico(no)
        return self._descartar(no.init, no.pos)

    def transformar_Atrib(self, no: Atrib) -> No | None:
        if no.nome in self.lidas:
            return self.generico(no)
        return self._descartar(no.valor, no.pos)


def _lidas(nos: list[No]) -> set[str]:
    return {n.nome for raiz in nos for n in percorrer(raiz) if isinstance(n, Nome)}


def _remover_variaveis_nao_lidas(p: Programa) -> Programa:
    itens: list[No] = []
    comandos = [i for i in p.itens if not isinstance(i, Funcao)]
    lidas_main = _lidas(comandos)
    for item in p.itens:
        if isinstance(item, Funcao):
            itens.append(_SemUso(_lidas([item.corpo])).transformar(item))
        else:
            r = _SemUso(lidas_main).transformar(item)
            if r is not None:
                itens.extend(r if isinstance(r, list) else [r])
    return Programa(itens, pos=p.pos)


def _remover_funcoes_inalcancaveis(p: Programa) -> Programa:
    por_nome = {f.nome: f for f in p.funcoes()}
    pendentes = [c.nome for i in p.comandos() for c in percorrer(i) if isinstance(c, Chamada)]
    vivas: set[str] = set()
    while pendentes:
        nome = pendentes.pop()
        if nome in vivas or nome not in por_nome:
            continue
        vivas.add(nome)
        pendentes.extend(c.nome for c in percorrer(por_nome[nome]) if isinstance(c, Chamada))
    return Programa([i for i in p.itens if not isinstance(i, Funcao) or i.nome in vivas],
                    pos=p.pos)


def eliminar_codigo_morto(programa: Programa) -> Programa:
    atual = programa
    while True:
        novo = _Limpador().transformar(atual)
        novo = _remover_variaveis_nao_lidas(novo)
        novo = _remover_funcoes_inalcancaveis(novo)
        if novo == atual:
            return novo
        atual = novo
