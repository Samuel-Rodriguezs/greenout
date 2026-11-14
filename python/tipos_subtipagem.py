"""Subtipagem estrutural: registros (largura e profundidade), funções,
listas, Top/Bot, junção (join) e interseção (meet) de tipos."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Top:
    pass


@dataclass(frozen=True)
class Bot:
    pass


@dataclass(frozen=True)
class Base:
    nome: str


@dataclass(frozen=True)
class Reg:
    campos: tuple[tuple[str, "Tipo"], ...]  # ordenado por nome

    def get(self, nome: str) -> "Tipo | None":
        return dict(self.campos).get(nome)


@dataclass(frozen=True)
class Fn:
    arg: "Tipo"
    res: "Tipo"


@dataclass(frozen=True)
class Lst:
    elem: "Tipo"


Tipo = Top | Bot | Base | Reg | Fn | Lst


def reg(**campos: Tipo) -> Reg:
    return Reg(tuple(sorted(campos.items())))


class Hierarquia:
    """Ordem parcial entre tipos base (Nat <: Int <: Num, por exemplo)."""

    def __init__(self, pares: list[tuple[str, str]] | None = None) -> None:
        self.pais: dict[str, set[str]] = {}
        for sub, sup in pares or []:
            self.declarar(sub, sup)

    def declarar(self, sub: str, sup: str) -> None:
        if sub != sup and sub in self.ancestrais(sup):
            raise ValueError(f"ciclo: {sup} já é subtipo de {sub}")
        self.pais.setdefault(sub, set()).add(sup)

    def ancestrais(self, nome: str) -> set[str]:
        vistos, pilha = {nome}, [nome]
        while pilha:
            for p in self.pais.get(pilha.pop(), ()):
                if p not in vistos:
                    vistos.add(p)
                    pilha.append(p)
        return vistos

    def todos(self) -> set[str]:
        r = set(self.pais)
        for ps in self.pais.values():
            r |= ps
        return r

    def sub(self, a: str, b: str) -> bool:
        return b in self.ancestrais(a)

    def uniao(self, a: str, b: str) -> str | None:
        comuns = self.ancestrais(a) & self.ancestrais(b)
        minimos = [c for c in comuns if all(self.sub(c, d) for d in comuns)]
        return minimos[0] if minimos else None

    def intersecao(self, a: str, b: str) -> str | None:
        comuns = {n for n in self.todos() | {a, b} if self.sub(n, a) and self.sub(n, b)}
        maximos = [c for c in comuns if all(self.sub(d, c) for d in comuns)]
        return maximos[0] if maximos else None


HIER_PADRAO = Hierarquia([("Nat", "Int"), ("Int", "Num"), ("Float", "Num")])


def subtipo(a: Tipo, b: Tipo, h: Hierarquia = HIER_PADRAO) -> bool:
    if isinstance(b, Top) or isinstance(a, Bot):
        return True
    if isinstance(a, Base) and isinstance(b, Base):
        return h.sub(a.nome, b.nome)
    if isinstance(a, Reg) and isinstance(b, Reg):
        for nome, tb in b.campos:
            ta = a.get(nome)
            if ta is None or not subtipo(ta, tb, h):
                return False
        return True
    if isinstance(a, Fn) and isinstance(b, Fn):
        return subtipo(b.arg, a.arg, h) and subtipo(a.res, b.res, h)
    if isinstance(a, Lst) and isinstance(b, Lst):
        return subtipo(a.elem, b.elem, h)
    return False


def juntar(a: Tipo, b: Tipo, h: Hierarquia = HIER_PADRAO) -> Tipo:
    """Menor supertipo comum (join)."""
    if subtipo(a, b, h):
        return b
    if subtipo(b, a, h):
        return a
    if isinstance(a, Base) and isinstance(b, Base):
        u = h.uniao(a.nome, b.nome)
        return Base(u) if u else Top()
    if isinstance(a, Reg) and isinstance(b, Reg):
        comuns = {n: juntar(t, b.get(n), h) for n, t in a.campos if b.get(n) is not None}
        return reg(**comuns)
    if isinstance(a, Fn) and isinstance(b, Fn):
        return Fn(intersectar(a.arg, b.arg, h), juntar(a.res, b.res, h))
    if isinstance(a, Lst) and isinstance(b, Lst):
        return Lst(juntar(a.elem, b.elem, h))
    return Top()


def intersectar(a: Tipo, b: Tipo, h: Hierarquia = HIER_PADRAO) -> Tipo:
    """Maior subtipo comum (meet)."""
    if subtipo(a, b, h):
        return a
    if subtipo(b, a, h):
        return b
    if isinstance(a, Base) and isinstance(b, Base):
        m = h.intersecao(a.nome, b.nome)
        return Base(m) if m else Bot()
    if isinstance(a, Reg) and isinstance(b, Reg):
        nomes = {n for n, _ in a.campos} | {n for n, _ in b.campos}
        campos: dict[str, Tipo] = {}
        for n in nomes:
            ta, tb = a.get(n), b.get(n)
            t = ta if tb is None else tb if ta is None else intersectar(ta, tb, h)
            if isinstance(t, Bot):
                return Bot()
            campos[n] = t
        return reg(**campos)
    if isinstance(a, Fn) and isinstance(b, Fn):
        return Fn(juntar(a.arg, b.arg, h), intersectar(a.res, b.res, h))
    if isinstance(a, Lst) and isinstance(b, Lst):
        return Lst(intersectar(a.elem, b.elem, h))
    return Bot()


def valor_tem_tipo(v: object, t: Tipo, h: Hierarquia = HIER_PADRAO) -> bool:
    """Checa em tempo de execução se um valor Python habita o tipo."""
    if isinstance(t, Top):
        return True
    if isinstance(t, Bot):
        return False
    if isinstance(t, Base):
        if isinstance(v, bool):
            return t.nome == "Bool"
        if isinstance(v, int):
            return h.sub("Nat" if v >= 0 else "Int", t.nome)
        if isinstance(v, float):
            return h.sub("Float", t.nome)
        return isinstance(v, str) and t.nome == "Str"
    if isinstance(t, Reg):
        return isinstance(v, dict) and all(
            n in v and valor_tem_tipo(v[n], ft, h) for n, ft in t.campos)
    if isinstance(t, Lst):
        return isinstance(v, list) and all(valor_tem_tipo(x, t.elem, h) for x in v)
    return callable(v)
