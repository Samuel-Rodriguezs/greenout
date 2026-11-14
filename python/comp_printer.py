"""Pretty printer da AST de Mini: devolve código-fonte canônico.

Propriedade garantida (testada): ``parse(formatar(parse(x))) == parse(x)``.
Também oferece ``dump`` para inspecionar a árvore de forma indentada.
"""
from __future__ import annotations

import dataclasses

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_parser import PRECEDENCIA, PREC_UNARIO

INDENT = "    "


def formatar_expr(e: No, minimo: int = 0) -> str:
    """Formata uma expressão; ``minimo`` é a precedência exigida pelo contexto."""
    if isinstance(e, Num):
        return str(e.valor)
    if isinstance(e, Bool):
        return "true" if e.valor else "false"
    if isinstance(e, Nome):
        return e.nome
    if isinstance(e, Chamada):
        return f"{e.nome}({', '.join(formatar_expr(a) for a in e.args)})"
    if isinstance(e, Unario):
        interno = e.operando
        texto = formatar_expr(interno, PREC_UNARIO)
        if isinstance(interno, Num) and interno.valor < 0:
            texto = f"({texto})"
        return e.op + texto
    if isinstance(e, Binario):
        prec = PRECEDENCIA[e.op]
        esq = formatar_expr(e.esq, prec - 1)
        dir_ = formatar_expr(e.dir, prec)
        texto = f"{esq} {e.op} {dir_}"
        return f"({texto})" if prec <= minimo else texto
    raise TypeError(f"não é expressão: {type(e).__name__}")


def _bloco(b: Bloco, nivel: int) -> list[str]:
    if not b.stmts:
        return ["{}"]
    linhas = ["{"]
    for s in b.stmts:
        linhas.extend(_stmt(s, nivel + 1))
    linhas.append(INDENT * nivel + "}")
    return linhas


def _anexar(prefixo: str, bloco_linhas: list[str]) -> list[str]:
    return [prefixo + bloco_linhas[0]] + bloco_linhas[1:]


def _stmt(s: No, nivel: int) -> list[str]:
    ind = INDENT * nivel
    if isinstance(s, Var):
        anot = f": {s.tipo}" if s.tipo else ""
        return [f"{ind}var {s.nome}{anot} = {formatar_expr(s.init)};"]
    if isinstance(s, Atrib):
        return [f"{ind}{s.nome} = {formatar_expr(s.valor)};"]
    if isinstance(s, Imprimir):
        return [f"{ind}print({formatar_expr(s.valor)});"]
    if isinstance(s, Retorno):
        return [f"{ind}return;" if s.valor is None
                else f"{ind}return {formatar_expr(s.valor)};"]
    if isinstance(s, ExprStmt):
        return [f"{ind}{formatar_expr(s.expr)};"]
    if isinstance(s, Bloco):
        return _anexar(ind, _bloco(s, nivel))
    if isinstance(s, Enquanto):
        return _anexar(f"{ind}while ({formatar_expr(s.cond)}) ", _bloco(s.corpo, nivel))
    if isinstance(s, Se):
        linhas = _anexar(f"{ind}if ({formatar_expr(s.cond)}) ", _bloco(s.entao, nivel))
        senao = s.senao
        if senao is not None:
            if len(senao.stmts) == 1 and isinstance(senao.stmts[0], Se):
                resto = _stmt(senao.stmts[0], nivel)
                resto[0] = resto[0].lstrip()
                linhas[-1] += " else " + resto[0]
                linhas.extend(resto[1:])
            else:
                linhas[-1] += " else " + _bloco(senao, nivel)[0]
                linhas.extend(_bloco(senao, nivel)[1:])
        return linhas
    if isinstance(s, Funcao):
        params = ", ".join(f"{p.nome}: {p.tipo}" for p in s.params)
        ret = "" if s.ret == "void" else f" -> {s.ret}"
        return _anexar(f"{ind}func {s.nome}({params}){ret} ", _bloco(s.corpo, nivel))
    raise TypeError(f"nó desconhecido: {type(s).__name__}")


def formatar(no: No) -> str:
    """Formata um programa, comando ou expressão como fonte Mini."""
    if isinstance(no, Programa):
        partes: list[str] = []
        for item in no.itens:
            partes.append("\n".join(_stmt(item, 0)))
        # linha em branco ao redor de funções
        saida: list[str] = []
        for i, p in enumerate(partes):
            if i and (isinstance(no.itens[i], Funcao) or isinstance(no.itens[i - 1], Funcao)):
                saida.append("")
            saida.append(p)
        return "\n".join(saida) + ("\n" if saida else "")
    if isinstance(no, (Num, Bool, Nome, Unario, Binario, Chamada)):
        return formatar_expr(no)
    return "\n".join(_stmt(no, 0))


def dump(no: object, nivel: int = 0) -> str:
    """Representação em árvore indentada (nome do nó e campos escalares)."""
    ind = "  " * nivel
    if isinstance(no, No):
        campos = dataclasses.fields(no)
        escalares = [f"{f.name}={getattr(no, f.name)!r}" for f in campos
                     if f.name != "pos"
                     and not isinstance(getattr(no, f.name), (No, list))
                     and getattr(no, f.name) is not None]
        cab = f"{ind}{type(no).__name__}" + (f"({', '.join(escalares)})" if escalares else "")
        linhas = [cab]
        for f in campos:
            v = getattr(no, f.name)
            if isinstance(v, No):
                linhas.append(dump(v, nivel + 1))
            elif isinstance(v, list):
                linhas.extend(dump(x, nivel + 1) for x in v)
        return "\n".join(linhas)
    return f"{ind}{no!r}"
