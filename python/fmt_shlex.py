"""Divisão de linha de comando em argumentos (estilo shell POSIX) e quoting."""
from __future__ import annotations

import re


class ErroShlex(ValueError):
    """Linha de comando malformada."""


def dividir(linha: str, comentarios: bool = False) -> list[str]:
    """Divide respeitando aspas simples, duplas e barra invertida.

    Dentro de aspas duplas, a barra só escapa \\, ", $ e `.
    """
    args: list[str] = []
    atual: list[str] = []
    em_token = False
    i, n = 0, len(linha)
    while i < n:
        c = linha[i]
        if c in " \t\r\n":
            if em_token:
                args.append("".join(atual))
                atual, em_token = [], False
            i += 1
        elif c == "#" and comentarios and not em_token:
            break
        elif c == "\\":
            if i + 1 >= n:
                raise ErroShlex("barra invertida no fim da linha")
            if linha[i + 1] != "\n":  # continuação de linha é descartada
                atual.append(linha[i + 1])
                em_token = True
            i += 2
        elif c == "'":
            fim = linha.find("'", i + 1)
            if fim == -1:
                raise ErroShlex("aspas simples não fechadas")
            atual.append(linha[i + 1:fim])
            em_token = True
            i = fim + 1
        elif c == '"':
            i += 1
            em_token = True
            while True:
                if i >= n:
                    raise ErroShlex("aspas duplas não fechadas")
                d = linha[i]
                if d == '"':
                    i += 1
                    break
                if d == "\\" and i + 1 < n and linha[i + 1] in '\\"$`':
                    atual.append(linha[i + 1])
                    i += 2
                elif d == "\\" and i + 1 < n and linha[i + 1] == "\n":
                    i += 2
                else:
                    atual.append(d)
                    i += 1
        else:
            atual.append(c)
            em_token = True
            i += 1
    if em_token:
        args.append("".join(atual))
    return args


def citar(arg: str) -> str:
    """Escapa um argumento para uso seguro no shell."""
    if arg == "":
        return "''"
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", arg):
        return arg
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def juntar(args: list[str]) -> str:
    return " ".join(citar(a) for a in args)
