"""Leitor e formatador (pretty printer) de S-expressions com quebra por largura."""
from __future__ import annotations

from typing import Union

Sexpr = Union[str, list["Sexpr"]]


class ErroSexpr(Exception):
    """S-expression mal formada."""


def _tokens(texto: str) -> list[str]:
    toks: list[str] = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c.isspace():
            i += 1
        elif c == ";":
            while i < len(texto) and texto[i] != "\n":
                i += 1
        elif c in "()":
            toks.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < len(texto) and texto[j] != '"':
                j += 2 if texto[j] == "\\" else 1
            if j >= len(texto):
                raise ErroSexpr("string não terminada")
            toks.append(texto[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < len(texto) and not texto[j].isspace() and texto[j] not in '()";':
                j += 1
            toks.append(texto[i:j])
            i = j
    return toks


def ler(texto: str) -> list[Sexpr]:
    """Lê todas as expressões de nível superior (átomos são strings)."""
    pilha: list[list[Sexpr]] = [[]]
    for t in _tokens(texto):
        if t == "(":
            pilha.append([])
        elif t == ")":
            if len(pilha) == 1:
                raise ErroSexpr("')' inesperado")
            lista = pilha.pop()
            pilha[-1].append(lista)
        else:
            pilha[-1].append(t)
    if len(pilha) != 1:
        raise ErroSexpr("'(' não fechado")
    return pilha[0]


def compacto(x: Sexpr) -> str:
    return x if isinstance(x, str) else "(" + " ".join(compacto(i) for i in x) + ")"


def formatar(x: Sexpr, largura: int = 40, indent: int = 0) -> str:
    """Formata cabendo em `largura` colunas, quebrando listas longas.

    Estilo: `(cabeça arg1` na primeira linha e os demais argumentos alinhados abaixo do primeiro,
    quando a cabeça é um átomo; senão, itens indentados em 1 coluna.
    """
    c = compacto(x)
    if isinstance(x, str) or indent + len(c) <= largura or not x:
        return c
    cabeca = x[0]
    if isinstance(cabeca, str):
        col = indent + 2 + len(cabeca)
        if len(x) == 1:
            return c
        linhas = [f"({cabeca} {formatar(x[1], largura, col)}"]
        for item in x[2:]:
            linhas.append(" " * col + formatar(item, largura, col))
        return "\n".join(linhas) + ")"
    col = indent + 1
    linhas = ["(" + formatar(cabeca, largura, col)]
    for item in x[1:]:
        linhas.append(" " * col + formatar(item, largura, col))
    return "\n".join(linhas) + ")"


def formatar_texto(texto: str, largura: int = 40) -> str:
    """Lê e formata todas as expressões, separadas por linha em branco."""
    return "\n\n".join(formatar(e, largura) for e in ler(texto))
