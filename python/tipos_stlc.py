"""Cálculo lambda simplesmente tipado: verificação (estilo Church, com
anotações) e inferência monomórfica (estilo Curry, via unificação)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import count

from tipos_unificacao import (BOOL, INT, ErroUnificacao, Subst, TCon, TVar,
                              Tipo, aplicar, seta, unificar, variaveis)


@dataclass(frozen=True)
class Var:
    nome: str


@dataclass(frozen=True)
class Lam:
    param: str
    anot: Tipo | None
    corpo: "Termo"


@dataclass(frozen=True)
class App:
    fun: "Termo"
    arg: "Termo"


@dataclass(frozen=True)
class Lit:
    valor: int | bool


@dataclass(frozen=True)
class Se:
    cond: "Termo"
    entao: "Termo"
    senao: "Termo"


Termo = Var | Lam | App | Lit | Se
Contexto = dict[str, Tipo]


class ErroTipo(Exception):
    pass


def _tipo_lit(v: int | bool) -> Tipo:
    return BOOL if isinstance(v, bool) else INT


def verificar(t: Termo, ctx: Contexto | None = None) -> Tipo:
    """Calcula o tipo de t; todas as lambdas precisam de anotação."""
    ctx = ctx or {}
    if isinstance(t, Var):
        if t.nome not in ctx:
            raise ErroTipo(f"variável não ligada: {t.nome}")
        return ctx[t.nome]
    if isinstance(t, Lit):
        return _tipo_lit(t.valor)
    if isinstance(t, Lam):
        if t.anot is None:
            raise ErroTipo(f"parâmetro {t.param} sem anotação")
        return seta(t.anot, verificar(t.corpo, {**ctx, t.param: t.anot}))
    if isinstance(t, App):
        f = verificar(t.fun, ctx)
        a = verificar(t.arg, ctx)
        if not (isinstance(f, TCon) and f.nome == "->"):
            raise ErroTipo("aplicação de valor que não é função")
        if f.args[0] != a:
            raise ErroTipo(f"argumento esperado {f.args[0]}, obtido {a}")
        return f.args[1]
    c = verificar(t.cond, ctx)
    if c != BOOL:
        raise ErroTipo("condição deve ser Bool")
    r1, r2 = verificar(t.entao, ctx), verificar(t.senao, ctx)
    if r1 != r2:
        raise ErroTipo("ramos com tipos diferentes")
    return r1


def inferir(t: Termo, ctx: Contexto | None = None) -> Tipo:
    """Tipo principal de t (variáveis de tipo renomeadas a, b, c...)."""
    frescas = count()
    s: Subst = {}

    def nova() -> TVar:
        return TVar(f"_t{next(frescas)}")

    def unir(a: Tipo, b: Tipo) -> None:
        nonlocal s
        try:
            s = unificar(a, b, s)
        except ErroUnificacao as e:
            raise ErroTipo(str(e)) from e

    def go(t: Termo, ctx: Contexto) -> Tipo:
        if isinstance(t, Var):
            if t.nome not in ctx:
                raise ErroTipo(f"variável não ligada: {t.nome}")
            return ctx[t.nome]
        if isinstance(t, Lit):
            return _tipo_lit(t.valor)
        if isinstance(t, Lam):
            p = t.anot if t.anot is not None else nova()
            return seta(p, go(t.corpo, {**ctx, t.param: p}))
        if isinstance(t, App):
            f = go(t.fun, ctx)
            a = go(t.arg, ctx)
            r = nova()
            unir(f, seta(a, r))
            return r
        unir(go(t.cond, ctx), BOOL)
        r1, r2 = go(t.entao, ctx), go(t.senao, ctx)
        unir(r1, r2)
        return r1

    resultado = aplicar(s, go(t, dict(ctx or {})))
    resultado = aplicar(s, resultado)
    return normalizar_variaveis(resultado)


def normalizar_variaveis(t: Tipo) -> Tipo:
    """Renomeia variáveis livres para a, b, c... pela ordem de aparição."""
    ordem: list[str] = []

    def coleta(t: Tipo) -> None:
        if isinstance(t, TVar):
            if t.nome not in ordem:
                ordem.append(t.nome)
        else:
            for a in t.args:
                coleta(a)

    coleta(t)
    nomes = {v: TVar(_nome_letra(i)) for i, v in enumerate(ordem)}

    def troca(t: Tipo) -> Tipo:
        if isinstance(t, TVar):
            return nomes[t.nome]
        return TCon(t.nome, tuple(troca(a) for a in t.args))

    return troca(t)


def _nome_letra(i: int) -> str:
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(97 + r) + s
    return s


def e_fechado_e_monomorfo(t: Tipo) -> bool:
    return not variaveis(t)
