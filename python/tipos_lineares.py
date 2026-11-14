"""Tipos lineares simples: valores de tipo linear devem ser usados
exatamente uma vez; valores ilimitados podem ser copiados e descartados."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Base:
    """Tipo ilimitado (Int, Bool, Unit...)."""
    nome: str


@dataclass(frozen=True)
class Recurso:
    """Tipo linear atômico (arquivo, conexão...)."""
    nome: str


@dataclass(frozen=True)
class Fn:
    arg: "Tipo"
    res: "Tipo"
    linear: bool = False


@dataclass(frozen=True)
class Tensor:
    a: "Tipo"
    b: "Tipo"


Tipo = Base | Recurso | Fn | Tensor
INT, BOOL, UNIT = Base("Int"), Base("Bool"), Base("Unit")


@dataclass(frozen=True)
class Var:
    nome: str


@dataclass(frozen=True)
class Lam:
    param: str
    tipo: Tipo
    corpo: "Termo"
    linear: bool = False


@dataclass(frozen=True)
class App:
    fun: "Termo"
    arg: "Termo"


@dataclass(frozen=True)
class Par:
    a: "Termo"
    b: "Termo"


@dataclass(frozen=True)
class LetPar:
    x: str
    y: str
    valor: "Termo"
    corpo: "Termo"


@dataclass(frozen=True)
class Let:
    nome: str
    valor: "Termo"
    corpo: "Termo"


@dataclass(frozen=True)
class Lit:
    valor: int | bool


@dataclass(frozen=True)
class Unidade:
    pass


@dataclass(frozen=True)
class Se:
    cond: "Termo"
    entao: "Termo"
    senao: "Termo"


Termo = Var | Lam | App | Par | LetPar | Let | Lit | Unidade | Se


class ErroLinear(Exception):
    pass


def e_linear(t: Tipo) -> bool:
    if isinstance(t, Base):
        return False
    if isinstance(t, Recurso):
        return True
    if isinstance(t, Fn):
        return t.linear
    return e_linear(t.a) or e_linear(t.b)


def _ligar(nome: str, tipo: Tipo, usos: Counter) -> None:
    """Fecha o escopo de uma variável: remove-a dos usos e confere linearidade."""
    n = usos.pop(nome, 0)
    if e_linear(tipo) and n != 1:
        quando = "não foi consumida" if n == 0 else f"foi usada {n} vezes"
        raise ErroLinear(f"variável linear {nome} {quando}")


def _tipar(t: Termo, ctx: dict[str, Tipo]) -> tuple[Tipo, Counter]:
    if isinstance(t, Var):
        if t.nome not in ctx:
            raise ErroLinear(f"variável não ligada: {t.nome}")
        return ctx[t.nome], Counter({t.nome: 1})
    if isinstance(t, Lit):
        return (BOOL if isinstance(t.valor, bool) else INT), Counter()
    if isinstance(t, Unidade):
        return UNIT, Counter()
    if isinstance(t, Lam):
        tb, u = _tipar(t.corpo, {**ctx, t.param: t.tipo})
        _ligar(t.param, t.tipo, u)
        captura = any(e_linear(ctx[v]) for v in u if v in ctx)
        return Fn(t.tipo, tb, t.linear or captura), u
    if isinstance(t, App):
        tf, u1 = _tipar(t.fun, ctx)
        ta, u2 = _tipar(t.arg, ctx)
        if not isinstance(tf, Fn):
            raise ErroLinear("aplicação de valor que não é função")
        if tf.arg != ta:
            raise ErroLinear(f"argumento esperado {tf.arg}, obtido {ta}")
        return tf.res, u1 + u2
    if isinstance(t, Par):
        ta, u1 = _tipar(t.a, ctx)
        tb, u2 = _tipar(t.b, ctx)
        return Tensor(ta, tb), u1 + u2
    if isinstance(t, LetPar):
        te, u1 = _tipar(t.valor, ctx)
        if not isinstance(te, Tensor):
            raise ErroLinear("desestruturação de valor que não é par")
        if t.x == t.y:
            raise ErroLinear("nomes repetidos na desestruturação")
        tb, u2 = _tipar(t.corpo, {**ctx, t.x: te.a, t.y: te.b})
        _ligar(t.x, te.a, u2)
        _ligar(t.y, te.b, u2)
        return tb, u1 + u2
    if isinstance(t, Let):
        te, u1 = _tipar(t.valor, ctx)
        tb, u2 = _tipar(t.corpo, {**ctx, t.nome: te})
        _ligar(t.nome, te, u2)
        return tb, u1 + u2
    tc, uc = _tipar(t.cond, ctx)
    if tc != BOOL:
        raise ErroLinear("condição deve ser Bool")
    t1, u1 = _tipar(t.entao, ctx)
    t2, u2 = _tipar(t.senao, ctx)
    if t1 != t2:
        raise ErroLinear("ramos com tipos diferentes")
    juntos = Counter()
    for v in set(u1) | set(u2):
        if v in ctx and e_linear(ctx[v]) and u1[v] != u2[v]:
            raise ErroLinear(f"recurso {v} usado de forma diferente nos ramos")
        juntos[v] = max(u1[v], u2[v])
    return t1, uc + juntos


def verificar(t: Termo, ctx: dict[str, Tipo] | None = None) -> Tipo:
    """Tipo de t; o contexto linear precisa ser consumido exatamente uma vez."""
    ctx = ctx or {}
    tipo, usos = _tipar(t, ctx)
    for nome, ty in ctx.items():
        if e_linear(ty) and usos[nome] != 1:
            raise ErroLinear(f"recurso {nome} usado {usos[nome]} vezes (esperado 1)")
    return tipo
