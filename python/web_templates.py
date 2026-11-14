"""Templates com herança de blocos, escape HTML automático, if/for e filtros.

Sintaxe: {{ x.y|filtro:"arg" }}, {% if x %}..{% else %}..{% endif %}, {% for i in xs %}..{% endfor %},
{% extends "base" %}, {% block nome %}..{% endblock %}, {# comentário #}.
"""
from __future__ import annotations

import html
import re
from typing import Any, Callable

_TOKEN = re.compile(r"(\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\})", re.S)


class ErroTemplate(Exception):
    pass


class Seguro(str):
    """String já escapada/confiável: não sofre novo escape."""


def _escapar(v: Any) -> str:
    return str(v) if isinstance(v, Seguro) else html.escape("" if v is None else str(v), quote=True)


FILTROS: dict[str, Callable[..., Any]] = {
    "upper": lambda v: str(v).upper(),
    "lower": lambda v: str(v).lower(),
    "title": lambda v: str(v).title(),
    "length": lambda v: len(v),
    "safe": lambda v: Seguro(str(v)),
    "default": lambda v, d="": d if v in (None, "", [], {}) else v,
    "join": lambda v, sep=", ": sep.join(str(x) for x in v),
    "trim": lambda v: str(v).strip(),
}


def _dividir(texto: str, sep: str) -> list[str]:
    """Divide por `sep` fora de aspas."""
    partes, atual, aspas = [], "", None
    for c in texto:
        if aspas:
            atual += c
            if c == aspas:
                aspas = None
        elif c in "\"'":
            aspas = c
            atual += c
        elif c == sep:
            partes.append(atual)
            atual = ""
        else:
            atual += c
    partes.append(atual)
    return [p.strip() for p in partes]


def _literal(expr: str) -> tuple[bool, Any]:
    if len(expr) >= 2 and expr[0] == expr[-1] and expr[0] in "\"'":
        return True, expr[1:-1]
    if re.fullmatch(r"-?\d+", expr):
        return True, int(expr)
    if re.fullmatch(r"-?\d+\.\d+", expr):
        return True, float(expr)
    return {"true": (True, True), "false": (True, False), "none": (True, None)}.get(
        expr.lower(), (False, None))


def _resolver(expr: str, ctx: dict[str, Any]) -> Any:
    eh, valor = _literal(expr)
    if eh:
        return valor
    atual: Any = ctx
    for i, parte in enumerate(expr.split(".")):
        if not parte.isidentifier():
            raise ErroTemplate(f"expressão inválida: {expr!r}")
        if isinstance(atual, dict):
            if parte not in atual:
                return None
            atual = atual[parte]
        elif i == 0:
            return None
        else:
            if parte.startswith("_"):
                raise ErroTemplate(f"acesso a atributo privado: {parte}")
            atual = getattr(atual, parte, None)
            if callable(atual):
                atual = atual()
        if atual is None:
            return None
    return atual


def _condicao(expr: str, ctx: dict[str, Any]) -> bool:
    expr = expr.strip()
    for op in (" or ", " and "):
        if op in expr:
            a, b = expr.split(op, 1)
            return (_condicao(a, ctx) or _condicao(b, ctx)) if op == " or " else \
                   (_condicao(a, ctx) and _condicao(b, ctx))
    if expr.startswith("not "):
        return not _condicao(expr[4:], ctx)
    for op in ("==", "!=", ">=", "<=", ">", "<"):
        if op in expr:
            a, b = (s.strip() for s in expr.split(op, 1))
            x, y = _resolver(a, ctx), _resolver(b, ctx)
            try:
                return {"==": x == y, "!=": x != y, ">=": x >= y, "<=": x <= y,
                        ">": x > y, "<": x < y}[op]
            except TypeError:
                return False
    return bool(_resolver(expr, ctx))


Nodo = tuple


def _parse(fonte: str) -> list[Nodo]:
    tokens = [t for t in _TOKEN.split(fonte) if t != ""]
    pos = 0

    def bloco(fins: tuple[str, ...]) -> tuple[list[Nodo], str | None]:
        nonlocal pos
        nodos: list[Nodo] = []
        while pos < len(tokens):
            t = tokens[pos]
            pos += 1
            if t.startswith("{#"):
                continue
            if t.startswith("{{"):
                partes = _dividir(t[2:-2].strip(), "|")
                filtros = []
                for f in partes[1:]:
                    nome, _, arg = f.partition(":")
                    nome = nome.strip()
                    if nome not in FILTROS:
                        raise ErroTemplate(f"filtro desconhecido: {nome}")
                    filtros.append((nome, arg.strip() or None))
                nodos.append(("var", partes[0], filtros))
            elif t.startswith("{%"):
                cmd = t[2:-2].strip()
                palavra = cmd.split(None, 1)[0] if cmd else ""
                if palavra in fins:
                    return nodos, cmd
                resto = cmd[len(palavra):].strip()
                if palavra == "extends":
                    nodos.append(("extends", resto.strip("\"'")))
                elif palavra == "block":
                    corpo, fim = bloco(("endblock",))
                    if fim is None:
                        raise ErroTemplate(f"block {resto} sem endblock")
                    nodos.append(("block", resto, corpo))
                elif palavra == "if":
                    entao, fim = bloco(("else", "endif"))
                    senao: list[Nodo] = []
                    if fim == "else":
                        senao, fim = bloco(("endif",))
                    if fim is None:
                        raise ErroTemplate("if sem endif")
                    nodos.append(("if", resto, entao, senao))
                elif palavra == "for":
                    m = re.fullmatch(r"(\w+) in (.+)", resto)
                    if not m:
                        raise ErroTemplate(f"for inválido: {resto!r}")
                    corpo, fim = bloco(("else", "endfor"))
                    vazio: list[Nodo] = []
                    if fim == "else":
                        vazio, fim = bloco(("endfor",))
                    if fim is None:
                        raise ErroTemplate("for sem endfor")
                    nodos.append(("for", m.group(1), m.group(2), corpo, vazio))
                else:
                    raise ErroTemplate(f"tag desconhecida: {palavra!r}")
            else:
                nodos.append(("texto", t))
        return nodos, None

    nodos, fim = bloco(())
    return nodos


class Ambiente:
    def __init__(self, templates: dict[str, str] | None = None, escapar: bool = True) -> None:
        self.fontes = dict(templates or {})
        self.escapar = escapar
        self._cache: dict[str, list[Nodo]] = {}

    def adicionar(self, nome: str, fonte: str) -> None:
        self.fontes[nome] = fonte
        self._cache.pop(nome, None)

    def _carregar(self, nome: str) -> list[Nodo]:
        if nome not in self._cache:
            if nome not in self.fontes:
                raise ErroTemplate(f"template não encontrado: {nome}")
            nodos = _parse(self.fontes[nome])
            if any(n[0] == "extends" for n in nodos[1:]):
                raise ErroTemplate("extends deve ser a primeira tag e aparecer uma única vez")
            self._cache[nome] = nodos
        return self._cache[nome]

    def renderizar(self, nome: str, **contexto: Any) -> str:
        return self._render_template(nome, contexto, {}, [nome])

    def renderizar_texto(self, fonte: str, **contexto: Any) -> str:
        return self._render_nodos(_parse(fonte), contexto, {})

    def _render_template(self, nome: str, ctx: dict[str, Any], sobrescritas: dict[str, list[Nodo]],
                         cadeia: list[str]) -> str:
        nodos = self._carregar(nome)
        if nodos and nodos[0][0] == "extends":
            pai = nodos[0][1]
            if pai in cadeia:
                raise ErroTemplate(f"herança circular: {' -> '.join(cadeia + [pai])}")
            proprios = {n[1]: n[2] for n in nodos if n[0] == "block"}
            return self._render_template(pai, ctx, {**proprios, **sobrescritas}, cadeia + [pai])
        return self._render_nodos(nodos, ctx, sobrescritas)

    def _render_nodos(self, nodos: list[Nodo], ctx: dict[str, Any],
                      sobrescritas: dict[str, list[Nodo]]) -> str:
        saida: list[str] = []
        for n in nodos:
            tipo = n[0]
            if tipo == "texto":
                saida.append(n[1])
            elif tipo == "var":
                v = _resolver(n[1], ctx)
                for nome, arg in n[2]:
                    v = FILTROS[nome](v) if arg is None else FILTROS[nome](v, _resolver(arg, ctx))
                saida.append(_escapar(v) if self.escapar else ("" if v is None else str(v)))
            elif tipo == "if":
                saida.append(self._render_nodos(n[2] if _condicao(n[1], ctx) else n[3], ctx, sobrescritas))
            elif tipo == "for":
                itens = _resolver(n[2], ctx) or []
                itens = list(itens)
                if not itens:
                    saida.append(self._render_nodos(n[4], ctx, sobrescritas))
                for i, item in enumerate(itens):
                    loop = {"indice": i + 1, "indice0": i, "primeiro": i == 0,
                            "ultimo": i == len(itens) - 1, "total": len(itens)}
                    saida.append(self._render_nodos(n[3], {**ctx, n[1]: item, "loop": loop}, sobrescritas))
            elif tipo == "block":
                saida.append(self._render_nodos(sobrescritas.get(n[1], n[2]), ctx, sobrescritas))
            elif tipo == "extends":
                raise ErroTemplate("extends deve ser a primeira tag do template")
        return "".join(saida)
