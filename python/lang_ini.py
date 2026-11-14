"""Parser de um subconjunto de INI/TOML: [seções], chave = valor, tipos básicos e listas."""
from __future__ import annotations

import re
from typing import Any


class ErroConfig(Exception):
    """Erro de sintaxe, com número da linha."""


_CHAVE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _sem_comentario(linha: str) -> str:
    em_str = False
    for i, c in enumerate(linha):
        if c == '"' and (i == 0 or linha[i - 1] != "\\"):
            em_str = not em_str
        elif c in "#;" and not em_str:
            return linha[:i]
    return linha


def _dividir_lista(s: str) -> list[str]:
    itens, atual, em_str = [], [], False
    for i, c in enumerate(s):
        if c == '"' and (i == 0 or s[i - 1] != "\\"):
            em_str = not em_str
        if c == "," and not em_str:
            itens.append("".join(atual))
            atual = []
        else:
            atual.append(c)
    resto = "".join(atual)
    if resto.strip() or itens:
        itens.append(resto)
    return itens


def _valor(txt: str, n: int) -> Any:
    txt = txt.strip()
    if not txt:
        raise ErroConfig(f"linha {n}: valor ausente")
    if txt.startswith('"'):
        if len(txt) < 2 or not txt.endswith('"'):
            raise ErroConfig(f"linha {n}: string não terminada")
        return txt[1:-1].replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
    if txt.startswith("["):
        if not txt.endswith("]"):
            raise ErroConfig(f"linha {n}: lista não fechada")
        interior = txt[1:-1].strip()
        if not interior:
            return []
        itens = _dividir_lista(interior)
        if itens and not itens[-1].strip():
            itens.pop()  # vírgula final
        return [_valor(x, n) for x in itens]
    if txt == "true":
        return True
    if txt == "false":
        return False
    try:
        return int(txt.replace("_", ""))
    except ValueError:
        pass
    try:
        return float(txt)
    except ValueError:
        return txt  # INI clássico: texto puro


def analisar(texto: str) -> dict[str, Any]:
    """Converte o texto em dict; chaves antes de qualquer seção ficam na raiz.

    Seções com ponto ([a.b]) criam dicts aninhados.
    """
    raiz: dict[str, Any] = {}
    atual = raiz
    secoes_vistas: set[str] = set()
    for n, bruta in enumerate(texto.splitlines(), 1):
        linha = _sem_comentario(bruta).strip()
        if not linha:
            continue
        if linha.startswith("["):
            if not linha.endswith("]"):
                raise ErroConfig(f"linha {n}: seção não fechada")
            nome = linha[1:-1].strip()
            partes = nome.split(".")
            if not nome or not all(_CHAVE.match(p) and p for p in partes):
                raise ErroConfig(f"linha {n}: nome de seção inválido {nome!r}")
            if nome in secoes_vistas:
                raise ErroConfig(f"linha {n}: seção duplicada {nome!r}")
            secoes_vistas.add(nome)
            atual = raiz
            for p in partes:
                atual = atual.setdefault(p, {})
                if not isinstance(atual, dict):
                    raise ErroConfig(f"linha {n}: conflito em {p!r}")
            continue
        if "=" not in linha:
            raise ErroConfig(f"linha {n}: esperado 'chave = valor'")
        chave, _, val = linha.partition("=")
        chave = chave.strip()
        if not _CHAVE.match(chave):
            raise ErroConfig(f"linha {n}: chave inválida {chave!r}")
        if chave in atual:
            raise ErroConfig(f"linha {n}: chave duplicada {chave!r}")
        atual[chave] = _valor(val, n)
    return raiz
