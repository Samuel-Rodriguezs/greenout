"""Parser de Mini: descendente recursivo para comandos e Pratt para expressões.

Segue a gramática EBNF documentada em comp_lexer. A precedência dos
operadores binários (todos associativos à esquerda) fica em ``PRECEDENCIA``;
operadores unários ligam mais forte que qualquer binário.
"""
from __future__ import annotations

from typing import Optional

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Param, Programa, Retorno,
                      Se, Unario, Var)
from comp_lexer import ErroMini, Token, TipoToken, tokenizar

PRECEDENCIA: dict[str, int] = {
    "||": 1, "&&": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6,
}
PREC_UNARIO = 7


class ErroSintaxe(ErroMini):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    # --- utilitários ------------------------------------------------------
    @property
    def atual(self) -> Token:
        return self.tokens[self.i]

    def espiar(self, k: int = 1) -> Token:
        return self.tokens[min(self.i + k, len(self.tokens) - 1)]

    def avancar(self) -> Token:
        t = self.tokens[self.i]
        if t.tipo is not TipoToken.EOF:
            self.i += 1
        return t

    def _descricao(self, t: Token) -> str:
        return "fim do arquivo" if t.tipo is TipoToken.EOF else f"'{t.lexema}'"

    def erro(self, esperado: str) -> ErroSintaxe:
        t = self.atual
        return ErroSintaxe(f"esperado {esperado}, encontrado {self._descricao(t)}",
                           t.linha, t.coluna, max(1, len(t.lexema)))

    def eh(self, lexema: str) -> bool:
        t = self.atual
        return t.lexema == lexema and t.tipo in (TipoToken.OP, TipoToken.KEYWORD)

    def aceitar(self, lexema: str) -> Optional[Token]:
        if self.eh(lexema):
            return self.avancar()
        return None

    def exigir(self, lexema: str) -> Token:
        if not self.eh(lexema):
            raise self.erro(f"'{lexema}'")
        return self.avancar()

    def identificador(self) -> Token:
        if self.atual.tipo is not TipoToken.ID:
            raise self.erro("identificador")
        return self.avancar()

    @staticmethod
    def _pos(t: Token) -> tuple[int, int]:
        return (t.linha, t.coluna)

    # --- declarações ------------------------------------------------------
    def programa(self) -> Programa:
        itens: list[No] = []
        while self.atual.tipo is not TipoToken.EOF:
            itens.append(self.funcao() if self.eh("func") else self.comando())
        return Programa(itens, pos=(1, 1))

    def tipo(self, permitir_void: bool) -> str:
        t = self.atual
        validos = ("int", "bool", "void") if permitir_void else ("int", "bool")
        if t.tipo is TipoToken.KEYWORD and t.lexema in validos:
            self.avancar()
            return t.lexema
        raise self.erro("tipo (" + ", ".join(validos) + ")")

    def funcao(self) -> Funcao:
        kw = self.exigir("func")
        nome = self.identificador()
        self.exigir("(")
        params: list[Param] = []
        if not self.eh(")"):
            while True:
                p = self.identificador()
                self.exigir(":")
                params.append(Param(p.lexema, self.tipo(False), pos=self._pos(p)))
                if not self.aceitar(","):
                    break
        self.exigir(")")
        ret = self.tipo(True) if self.aceitar("->") else "void"
        corpo = self.bloco()
        return Funcao(nome.lexema, params, ret, corpo, pos=self._pos(nome))

    # --- comandos ---------------------------------------------------------
    def bloco(self) -> Bloco:
        abre = self.exigir("{")
        stmts: list[No] = []
        while not self.eh("}"):
            if self.atual.tipo is TipoToken.EOF:
                raise self.erro("'}'")
            stmts.append(self.comando())
        self.exigir("}")
        return Bloco(stmts, pos=self._pos(abre))

    def comando(self) -> No:
        t = self.atual
        if self.eh("func"):
            raise ErroSintaxe("funções só podem ser declaradas no nível superior",
                              t.linha, t.coluna, 4)
        if self.eh("var"):
            return self.decl()
        if self.eh("if"):
            return self.se()
        if self.eh("while"):
            self.avancar()
            cond = self.condicao()
            return Enquanto(cond, self.bloco(), pos=self._pos(t))
        if self.eh("return"):
            self.avancar()
            valor = None if self.eh(";") else self.expressao()
            self.exigir(";")
            return Retorno(valor, pos=self._pos(t))
        if self.eh("print"):
            self.avancar()
            self.exigir("(")
            valor = self.expressao()
            self.exigir(")")
            self.exigir(";")
            return Imprimir(valor, pos=self._pos(t))
        if self.eh("{"):
            return self.bloco()
        if t.tipo is TipoToken.ID and self.espiar().lexema == "=" \
                and self.espiar().tipo is TipoToken.OP:
            self.avancar()
            self.avancar()
            valor = self.expressao()
            self.exigir(";")
            return Atrib(t.lexema, valor, pos=self._pos(t))
        expr = self.expressao()
        self.exigir(";")
        return ExprStmt(expr, pos=expr.pos)

    def decl(self) -> Var:
        kw = self.exigir("var")
        nome = self.identificador()
        tipo = self.tipo(False) if self.aceitar(":") else None
        self.exigir("=")
        init = self.expressao()
        self.exigir(";")
        return Var(nome.lexema, init, tipo, pos=self._pos(nome))

    def condicao(self) -> No:
        self.exigir("(")
        cond = self.expressao()
        self.exigir(")")
        return cond

    def se(self) -> Se:
        kw = self.exigir("if")
        cond = self.condicao()
        entao = self.bloco()
        senao: Optional[Bloco] = None
        if self.aceitar("else"):
            if self.eh("if"):
                interno = self.se()
                senao = Bloco([interno], pos=interno.pos)
            else:
                senao = self.bloco()
        return Se(cond, entao, senao, pos=self._pos(kw))

    # --- expressões (Pratt) ----------------------------------------------
    def expressao(self, minimo: int = 0) -> No:
        esq = self.prefixo()
        while True:
            t = self.atual
            prec = PRECEDENCIA.get(t.lexema, 0) if t.tipo is TipoToken.OP else 0
            if prec <= minimo:
                return esq
            self.avancar()
            dir_ = self.expressao(prec)  # recursão com prec => assoc. à esquerda
            esq = Binario(t.lexema, esq, dir_, pos=self._pos(t))

    def prefixo(self) -> No:
        t = self.atual
        if t.tipo is TipoToken.NUM:
            self.avancar()
            return Num(int(t.lexema), pos=self._pos(t))
        if t.tipo is TipoToken.KEYWORD and t.lexema in ("true", "false"):
            self.avancar()
            return Bool(t.lexema == "true", pos=self._pos(t))
        if t.tipo is TipoToken.ID:
            self.avancar()
            if self.aceitar("("):
                args: list[No] = []
                if not self.eh(")"):
                    while True:
                        args.append(self.expressao())
                        if not self.aceitar(","):
                            break
                self.exigir(")")
                return Chamada(t.lexema, args, pos=self._pos(t))
            return Nome(t.lexema, pos=self._pos(t))
        if t.tipo is TipoToken.OP and t.lexema in ("-", "!"):
            self.avancar()
            return Unario(t.lexema, self.expressao(PREC_UNARIO), pos=self._pos(t))
        if self.aceitar("("):
            e = self.expressao()
            self.exigir(")")
            return e
        raise self.erro("expressão")


def parse(fonte: str) -> Programa:
    """Analisa um programa Mini completo."""
    p = Parser(tokenizar(fonte))
    return p.programa()


def parse_expressao(fonte: str) -> No:
    """Analisa o fonte inteiro como uma única expressão."""
    p = Parser(tokenizar(fonte))
    e = p.expressao()
    if p.atual.tipo is not TipoToken.EOF:
        raise p.erro("fim da expressão")
    return e
