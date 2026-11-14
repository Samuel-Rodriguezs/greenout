"""Codificação e decodificação de query strings (application/x-www-form-urlencoded)."""
from __future__ import annotations

from typing import Any

_SEGUROS = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~")


class ErroQuery(ValueError):
    """Query string malformada."""


def codificar_valor(s: str) -> str:
    """Codifica percentualmente (espaço vira '+')."""
    saida: list[str] = []
    for b in s.encode("utf-8"):
        if b in _SEGUROS:
            saida.append(chr(b))
        elif b == 0x20:
            saida.append("+")
        else:
            saida.append(f"%{b:02X}")
    return "".join(saida)


def decodificar_valor(s: str) -> str:
    bruto = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "%":
            h = s[i + 1:i + 3]
            if len(h) != 2 or any(x not in "0123456789abcdefABCDEF" for x in h):
                raise ErroQuery(f"escape inválido: {s[i:i + 3]!r}")
            bruto.append(int(h, 16))
            i += 3
        else:
            bruto.extend(b" " if c == "+" else c.encode("utf-8"))
            i += 1
    try:
        return bruto.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ErroQuery("bytes não são UTF-8 válido") from e


def decodificar(query: str) -> dict[str, Any]:
    """Decodifica; chaves repetidas ou 'k[]' viram lista, 'a[b]' vira dict aninhado."""
    query = query.lstrip("?")
    res: dict[str, Any] = {}
    for par in query.split("&"):
        if not par:
            continue
        k, _, v = par.partition("=")
        chave, valor = decodificar_valor(k), decodificar_valor(v)
        if not chave:
            raise ErroQuery("chave vazia")
        _inserir(res, chave, valor)
    return res


def _inserir(res: dict[str, Any], chave: str, valor: str) -> None:
    if "[" in chave and chave.endswith("]") and not chave.startswith("["):
        base, resto = chave.split("[", 1)
        sub = resto[:-1]
        if "[" in sub or "]" in sub:
            raise ErroQuery(f"chave aninhada inválida: {chave!r}")
        if sub == "":
            atual = res.setdefault(base, [])
            if not isinstance(atual, list):
                atual = res[base] = [atual]
            atual.append(valor)
        else:
            atual = res.setdefault(base, {})
            if not isinstance(atual, dict):
                raise ErroQuery(f"conflito na chave {base!r}")
            atual[sub] = valor
        return
    if chave in res:
        if isinstance(res[chave], list):
            res[chave].append(valor)
        elif isinstance(res[chave], dict):
            raise ErroQuery(f"conflito na chave {chave!r}")
        else:
            res[chave] = [res[chave], valor]
    else:
        res[chave] = valor


def codificar(dados: dict[str, Any]) -> str:
    """Codifica dicionário (listas viram chaves repetidas, dicts viram 'a[b]=v')."""
    partes: list[str] = []
    for k, v in dados.items():
        ck = codificar_valor(str(k))
        if isinstance(v, (list, tuple)):
            partes += [f"{ck}={codificar_valor(_str(x))}" for x in v]
        elif isinstance(v, dict):
            partes += [f"{ck}%5B{codificar_valor(str(s))}%5D={codificar_valor(_str(x))}" for s, x in v.items()]
        else:
            partes.append(f"{ck}={codificar_valor(_str(v))}")
    return "&".join(partes)


def _str(v: Any) -> str:
    if v is True:
        return "true"
    if v is False:
        return "false"
    return "" if v is None else str(v)
