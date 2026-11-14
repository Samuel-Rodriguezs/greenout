"""Unificação de tipos de Robinson com occurs check."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TVar:
    nome: str


@dataclass(frozen=True)
class TCon:
    nome: str
    args: tuple["Tipo", ...] = ()


Tipo = TVar | TCon
Subst = dict[str, Tipo]

INT = TCon("Int")
BOOL = TCon("Bool")


def seta(a: Tipo, b: Tipo) -> TCon:
    return TCon("->", (a, b))


def lista(a: Tipo) -> TCon:
    return TCon("List", (a,))


def par(a: Tipo, b: Tipo) -> TCon:
    return TCon("*", (a, b))


class ErroUnificacao(Exception):
    pass


def aplicar(s: Subst, t: Tipo) -> Tipo:
    """Aplica a substituição (idempotente ou encadeada) a um tipo."""
    if isinstance(t, TVar):
        if t.nome in s:
            return aplicar(s, s[t.nome])
        return t
    return TCon(t.nome, tuple(aplicar(s, a) for a in t.args))


def variaveis(t: Tipo) -> set[str]:
    if isinstance(t, TVar):
        return {t.nome}
    return set().union(*(variaveis(a) for a in t.args)) if t.args else set()


def compor(s2: Subst, s1: Subst) -> Subst:
    """Substituição que aplica s1 e depois s2."""
    r = {k: aplicar(s2, v) for k, v in s1.items()}
    for k, v in s2.items():
        r.setdefault(k, v)
    return r


def unificar(a: Tipo, b: Tipo, s: Subst | None = None) -> Subst:
    """Retorna o unificador mais geral estendendo `s`, ou levanta ErroUnificacao."""
    s = dict(s or {})
    pilha = [(a, b)]
    while pilha:
        x, y = pilha.pop()
        x, y = aplicar(s, x), aplicar(s, y)
        if x == y:
            continue
        if isinstance(x, TVar) or isinstance(y, TVar):
            v, t = (x, y) if isinstance(x, TVar) else (y, x)
            if v.nome in variaveis(t):
                raise ErroUnificacao(f"occurs check: {v.nome} em {mostrar(t)}")
            s = compor({v.nome: t}, s)
            continue
        if x.nome != y.nome or len(x.args) != len(y.args):
            raise ErroUnificacao(f"não unifica: {mostrar(x)} e {mostrar(y)}")
        pilha.extend(zip(x.args, y.args))
    return s


def unificar_todos(pares: list[tuple[Tipo, Tipo]]) -> Subst:
    s: Subst = {}
    for a, b in pares:
        s = unificar(a, b, s)
    return s


def mostrar(t: Tipo) -> str:
    if isinstance(t, TVar):
        return "'" + t.nome
    if t.nome == "->":
        a, b = t.args
        esq = mostrar(a)
        if isinstance(a, TCon) and a.nome == "->":
            esq = f"({esq})"
        return f"{esq} -> {mostrar(b)}"
    if t.nome == "*":
        return f"({mostrar(t.args[0])} * {mostrar(t.args[1])})"
    if not t.args:
        return t.nome
    return f"{t.nome}<{', '.join(mostrar(a) for a in t.args)}>"
