"""JSON Pointer (RFC 6901) e um JSONPath mínimo ($, .chave, ['chave'], [n], [*], .*, ..chave, [a:b])."""
from __future__ import annotations

import re
from typing import Any


class ErroPonteiro(ValueError):
    """Ponteiro/caminho inválido ou valor não encontrado."""


# ---------------- JSON Pointer ----------------

def dividir_ponteiro(ponteiro: str) -> list[str]:
    if ponteiro == "":
        return []
    if not ponteiro.startswith("/"):
        raise ErroPonteiro(f"ponteiro deve começar com '/': {ponteiro!r}")
    partes = ponteiro[1:].split("/")
    res = []
    for p in partes:
        if re.search(r"~(?![01])", p):
            raise ErroPonteiro(f"escape '~' inválido em {p!r}")
        res.append(p.replace("~1", "/").replace("~0", "~"))
    return res


def montar_ponteiro(partes: list[str]) -> str:
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in partes)


def _indice(parte: str, tam: int, permite_fim: bool = False) -> int:
    if parte == "-" and permite_fim:
        return tam
    if not re.fullmatch(r"0|[1-9]\d*", parte):
        raise ErroPonteiro(f"índice de lista inválido: {parte!r}")
    i = int(parte)
    if i > tam or (i == tam and not permite_fim):
        raise ErroPonteiro(f"índice fora do intervalo: {i}")
    return i


def resolver(doc: Any, ponteiro: str) -> Any:
    atual = doc
    for p in dividir_ponteiro(ponteiro):
        if isinstance(atual, dict):
            if p not in atual:
                raise ErroPonteiro(f"chave inexistente: {p!r}")
            atual = atual[p]
        elif isinstance(atual, list):
            atual = atual[_indice(p, len(atual))]
        else:
            raise ErroPonteiro(f"não é possível descer em {type(atual).__name__}")
    return atual


def definir(doc: Any, ponteiro: str, valor: Any) -> Any:
    """Retorna cópia de `doc` com o valor definido/inserido ('-' acrescenta ao fim de uma lista)."""
    import copy
    partes = dividir_ponteiro(ponteiro)
    if not partes:
        return valor
    novo = copy.deepcopy(doc)
    pai = resolver(novo, montar_ponteiro(partes[:-1]))
    ultimo = partes[-1]
    if isinstance(pai, dict):
        pai[ultimo] = valor
    elif isinstance(pai, list):
        i = _indice(ultimo, len(pai), True)
        pai.insert(i, valor)
    else:
        raise ErroPonteiro("o pai não é objeto nem lista")
    return novo


# ---------------- JSONPath mínimo ----------------

def _tokens(caminho: str) -> list[tuple[str, Any]]:
    if not caminho.startswith("$"):
        raise ErroPonteiro("o caminho deve começar com '$'")
    i, n = 1, len(caminho)
    toks: list[tuple[str, Any]] = []
    while i < n:
        if caminho.startswith("..", i):
            m = re.compile(r"\.\.([A-Za-z_]\w*|\*)").match(caminho, i)
            if not m:
                raise ErroPonteiro(f"descendente inválido em {i}")
            toks.append(("desc", m.group(1)))
            i = m.end()
        elif caminho[i] == ".":
            m = re.compile(r"\.([A-Za-z_][\w-]*|\*)").match(caminho, i)
            if not m:
                raise ErroPonteiro(f"nome esperado após '.' na posição {i}")
            toks.append(("todos",) if m.group(1) == "*" else ("chave", m.group(1)))  # type: ignore[arg-type]
            i = m.end()
        elif caminho[i] == "[":
            m = re.compile(r"\[\s*(?:(\*)|'([^']*)'|\"([^\"]*)\"|(-?\d+)|(-?\d*):(-?\d*))\s*\]").match(caminho, i)
            if not m:
                raise ErroPonteiro(f"colchetes inválidos na posição {i}")
            estrela, s1, s2, num, a, b = m.groups()
            if estrela:
                toks.append(("todos",))  # type: ignore[arg-type]
            elif s1 is not None or s2 is not None:
                toks.append(("chave", s1 if s1 is not None else s2))
            elif num is not None:
                toks.append(("indice", int(num)))
            else:
                toks.append(("fatia", (int(a) if a else None, int(b) if b else None)))
            i = m.end()
        else:
            raise ErroPonteiro(f"caractere inesperado {caminho[i]!r} na posição {i}")
    return toks


def _descendentes(v: Any) -> list[Any]:
    res = [v]
    filhos = v.values() if isinstance(v, dict) else v if isinstance(v, list) else []
    for f in filhos:
        res.extend(_descendentes(f))
    return res


def consultar(doc: Any, caminho: str) -> list[Any]:
    """Retorna a lista de valores que casam; caminhos sem correspondência dão lista vazia."""
    atuais = [doc]
    for tok in _tokens(caminho):
        tipo = tok[0]
        prox: list[Any] = []
        for v in atuais:
            if tipo == "chave":
                if isinstance(v, dict) and tok[1] in v:
                    prox.append(v[tok[1]])
            elif tipo == "indice":
                if isinstance(v, list) and -len(v) <= tok[1] < len(v):
                    prox.append(v[tok[1]])
            elif tipo == "fatia":
                if isinstance(v, list):
                    prox.extend(v[slice(*tok[1])])
            elif tipo == "todos":
                if isinstance(v, dict):
                    prox.extend(v.values())
                elif isinstance(v, list):
                    prox.extend(v)
            else:  # desc
                for d in _descendentes(v):
                    if tok[1] == "*":
                        if d is not v:
                            prox.append(d)
                    elif isinstance(d, dict) and tok[1] in d:
                        prox.append(d[tok[1]])
        atuais = prox
    return atuais
