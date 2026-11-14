"""Leitor CSV com inferência e conversão de tipos (int, float, bool, date, str)."""
from __future__ import annotations

import csv
import io
import re
from datetime import date
from typing import Any

_INT = re.compile(r"^[+-]?\d+$")
_FLOAT = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VERDADEIRO = {"true", "sim", "verdadeiro", "yes"}
_FALSO = {"false", "nao", "não", "falso", "no"}
TIPOS = ("int", "float", "bool", "date", "str")


def _normalizar_decimal(s: str, decimal: str) -> str:
    if decimal == ",":
        return s.replace(".", "").replace(",", ".")
    return s


def _eh_int(s: str) -> bool:
    return bool(_INT.match(s))


def _eh_float(s: str, decimal: str) -> bool:
    return bool(_FLOAT.match(_normalizar_decimal(s, decimal)))


def _eh_bool(s: str) -> bool:
    return s.lower() in _VERDADEIRO | _FALSO


def _eh_data(s: str) -> bool:
    if not _DATA.match(s):
        return False
    try:
        date.fromisoformat(s)
    except ValueError:
        return False
    return True


def inferir_tipo(valores: list[str], decimal: str = ".") -> str:
    """Menor tipo que acomoda todos os valores não vazios."""
    cheios = [v.strip() for v in valores if v is not None and v.strip() != ""]
    if not cheios:
        return "str"
    if all(_eh_int(v) for v in cheios):
        return "int"
    if all(_eh_int(v) or _eh_float(v, decimal) for v in cheios):
        return "float"
    if all(_eh_bool(v) for v in cheios):
        return "bool"
    if all(_eh_data(v) for v in cheios):
        return "date"
    return "str"


def converter(valor: str | None, tipo: str, decimal: str = ".") -> Any:
    if tipo not in TIPOS:
        raise ValueError(f"tipo desconhecido: {tipo}")
    if valor is None or valor.strip() == "":
        return None
    v = valor.strip()
    if tipo == "str":
        return valor
    if tipo == "int":
        if not _eh_int(v):
            raise ValueError(f"inteiro inválido: {v!r}")
        return int(v)
    if tipo == "float":
        if not (_eh_int(v) or _eh_float(v, decimal)):
            raise ValueError(f"decimal inválido: {v!r}")
        return float(_normalizar_decimal(v, decimal))
    if tipo == "bool":
        if not _eh_bool(v):
            raise ValueError(f"booleano inválido: {v!r}")
        return v.lower() in _VERDADEIRO
    if not _eh_data(v):
        raise ValueError(f"data inválida: {v!r}")
    return date.fromisoformat(v)


def ler_csv(
    texto: str,
    esquema: dict[str, str] | None = None,
    sep: str = ",",
    decimal: str = ".",
) -> list[dict[str, Any]]:
    """Lê CSV com cabeçalho. Colunas fora do esquema têm o tipo inferido."""
    leitor = csv.reader(io.StringIO(texto), delimiter=sep)
    linhas = [l for l in leitor if l]
    if not linhas:
        return []
    cab = [c.strip() for c in linhas[0]]
    corpo = linhas[1:]
    for n, l in enumerate(corpo, start=2):
        if len(l) != len(cab):
            raise ValueError(f"linha {n}: esperadas {len(cab)} colunas, achadas {len(l)}")
    tipos = {}
    for i, c in enumerate(cab):
        if esquema and c in esquema:
            tipos[c] = esquema[c]
        else:
            tipos[c] = inferir_tipo([l[i] for l in corpo], decimal)
    saida = []
    for n, l in enumerate(corpo, start=2):
        reg = {}
        for i, c in enumerate(cab):
            try:
                reg[c] = converter(l[i], tipos[c], decimal)
            except ValueError as e:
                raise ValueError(f"linha {n}, coluna {c}: {e}") from None
        saida.append(reg)
    return saida
