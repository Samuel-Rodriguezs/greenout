"""Args Kata (Uncle Bob): parser de argumentos de linha de comando com schema.

Schema: "l,p#,d*,n##" -> l booleano, p inteiro (#), d string (*), n float (##).
Argumentos: "-l -p 8080 -d /usr/logs".
"""
from __future__ import annotations

from typing import Any


class ErroArgs(ValueError):
    pass


_TIPOS = {"": "bool", "#": "int", "##": "float", "*": "str"}
_PADROES: dict[str, Any] = {"bool": False, "int": 0, "float": 0.0, "str": ""}


def _parse_schema(schema: str) -> dict[str, str]:
    resultado: dict[str, str] = {}
    for item in filter(None, (s.strip() for s in schema.split(","))):
        flag = item.rstrip("#*")
        sufixo = item[len(flag):]
        if len(flag) != 1 or not flag.isalpha():
            raise ErroArgs(f"flag inválida no schema: {item!r}")
        if sufixo not in _TIPOS:
            raise ErroArgs(f"tipo inválido no schema: {item!r}")
        if flag in resultado:
            raise ErroArgs(f"flag duplicada no schema: {flag}")
        resultado[flag] = _TIPOS[sufixo]
    return resultado


def _converter(flag: str, tipo: str, valor: str) -> Any:
    try:
        if tipo == "int":
            return int(valor)
        if tipo == "float":
            return float(valor)
    except ValueError:
        raise ErroArgs(f"valor inválido para -{flag}: {valor!r}") from None
    return valor


def parse(schema: str, argumentos: list[str]) -> dict[str, Any]:
    tipos = _parse_schema(schema)
    valores = {f: _PADROES[t] for f, t in tipos.items()}
    vistos: set[str] = set()
    i = 0
    while i < len(argumentos):
        arg = argumentos[i]
        if not (arg.startswith("-") and len(arg) == 2 and arg[1].isalpha()):
            raise ErroArgs(f"argumento inesperado: {arg!r}")
        flag = arg[1]
        if flag not in tipos:
            raise ErroArgs(f"flag desconhecida: -{flag}")
        if flag in vistos:
            raise ErroArgs(f"flag repetida: -{flag}")
        vistos.add(flag)
        if tipos[flag] == "bool":
            valores[flag] = True
            i += 1
            continue
        if i + 1 >= len(argumentos) or (
            argumentos[i + 1].startswith("-") and len(argumentos[i + 1]) == 2
            and argumentos[i + 1][1].isalpha()
        ):
            raise ErroArgs(f"valor ausente para -{flag}")
        valores[flag] = _converter(flag, tipos[flag], argumentos[i + 1])
        i += 2
    return valores
