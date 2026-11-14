"""Termos do cálculo lambda: variáveis livres, substituição sem captura,
alfa-equivalência, impressão e análise sintática."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    nome: str


@dataclass(frozen=True)
class Abs:
    param: str
    corpo: "Termo"


@dataclass(frozen=True)
class App:
    fun: "Termo"
    arg: "Termo"


Termo = Var | Abs | App


def livres(t: Termo) -> frozenset[str]:
    if isinstance(t, Var):
        return frozenset({t.nome})
    if isinstance(t, Abs):
        return livres(t.corpo) - {t.param}
    return livres(t.fun) | livres(t.arg)


def nome_fresco(base: str, evitar: frozenset[str] | set[str]) -> str:
    base = base.rstrip("0123456789") or "v"
    i = 1
    while f"{base}{i}" in evitar:
        i += 1
    return f"{base}{i}"


def substituir(t: Termo, x: str, s: Termo) -> Termo:
    """Calcula t[x := s] evitando a captura de variáveis livres de s."""
    if isinstance(t, Var):
        return s if t.nome == x else t
    if isinstance(t, App):
        return App(substituir(t.fun, x, s), substituir(t.arg, x, s))
    if t.param == x:
        return t
    if t.param in livres(s) and x in livres(t.corpo):
        novo = nome_fresco(t.param, livres(s) | livres(t.corpo) | {x})
        corpo = substituir(t.corpo, t.param, Var(novo))
        return Abs(novo, substituir(corpo, x, s))
    return Abs(t.param, substituir(t.corpo, x, s))


def alfa_equivalentes(a: Termo, b: Termo) -> bool:
    def go(a: Termo, b: Termo, ea: dict[str, int], eb: dict[str, int], n: int) -> bool:
        if isinstance(a, Var) and isinstance(b, Var):
            ia, ib = ea.get(a.nome), eb.get(b.nome)
            if ia is None and ib is None:
                return a.nome == b.nome
            return ia == ib
        if isinstance(a, Abs) and isinstance(b, Abs):
            return go(a.corpo, b.corpo, {**ea, a.param: n}, {**eb, b.param: n}, n + 1)
        if isinstance(a, App) and isinstance(b, App):
            return go(a.fun, b.fun, ea, eb, n) and go(a.arg, b.arg, ea, eb, n)
        return False

    return go(a, b, {}, {}, 0)


def mostrar(t: Termo) -> str:
    if isinstance(t, Var):
        return t.nome
    if isinstance(t, Abs):
        return f"λ{t.param}.{mostrar(t.corpo)}"
    f = mostrar(t.fun)
    if isinstance(t.fun, Abs):
        f = f"({f})"
    a = mostrar(t.arg)
    if isinstance(t.arg, (App, Abs)):
        a = f"({a})"
    return f"{f} {a}"


_TOKEN = re.compile(r"\s*(?:([\\λ.()])|([A-Za-z_][A-Za-z0-9_']*))")


def _tokens(texto: str) -> list[str]:
    saida, pos = [], 0
    texto = texto.rstrip()
    while pos < len(texto):
        m = _TOKEN.match(texto, pos)
        if not m:
            raise ValueError(f"caractere inesperado em {pos}: {texto[pos:pos + 1]!r}")
        saida.append(m.group(1) or m.group(2))
        pos = m.end()
    return saida


def analisar(texto: str) -> Termo:
    """Aceita `\\x y.corpo` ou `λx.corpo`; aplicação associa à esquerda."""
    toks = _tokens(texto)
    pos = 0

    def olhar() -> str | None:
        return toks[pos] if pos < len(toks) else None

    def comer(esperado: str | None = None) -> str:
        nonlocal pos
        if pos >= len(toks):
            raise ValueError("fim inesperado da entrada")
        t = toks[pos]
        if esperado is not None and t != esperado:
            raise ValueError(f"esperado {esperado!r}, obtido {t!r}")
        pos += 1
        return t

    def abstracao() -> Termo:
        comer()
        params = []
        while olhar() not in (".", None):
            p = comer()
            if not (p[0].isalpha() or p[0] == "_"):
                raise ValueError(f"parâmetro inválido: {p!r}")
            params.append(p)
        if not params:
            raise ValueError("abstração sem parâmetros")
        comer(".")
        corpo = termo()
        for p in reversed(params):
            corpo = Abs(p, corpo)
        return corpo

    def atomo() -> Termo:
        t = olhar()
        if t == "(":
            comer()
            r = termo()
            comer(")")
            return r
        if t in ("\\", "λ"):
            return abstracao()
        if t is None or t in (")", "."):
            raise ValueError(f"token inesperado: {t!r}")
        return Var(comer())

    def termo() -> Termo:
        r = atomo()
        while olhar() not in (None, ")"):
            r = App(r, atomo())
        return r

    r = termo()
    if pos != len(toks):
        raise ValueError(f"sobra entrada: {toks[pos]!r}")
    return r
