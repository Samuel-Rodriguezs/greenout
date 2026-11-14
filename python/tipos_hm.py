"""Hindley-Milner com o Algoritmo W e let-polimorfismo."""
from __future__ import annotations

from dataclasses import dataclass

from tipos_stlc import ErroTipo, normalizar_variaveis
from tipos_unificacao import (BOOL, INT, ErroUnificacao, Subst, TCon, TVar,
                              Tipo, aplicar, compor, par, seta, unificar,
                              variaveis)


@dataclass(frozen=True)
class EVar:
    nome: str


@dataclass(frozen=True)
class ELam:
    param: str
    corpo: "Expr"


@dataclass(frozen=True)
class EApp:
    fun: "Expr"
    arg: "Expr"


@dataclass(frozen=True)
class ELet:
    nome: str
    valor: "Expr"
    corpo: "Expr"


@dataclass(frozen=True)
class ELit:
    valor: int | bool


@dataclass(frozen=True)
class ESe:
    cond: "Expr"
    entao: "Expr"
    senao: "Expr"


Expr = EVar | ELam | EApp | ELet | ELit | ESe


@dataclass(frozen=True)
class Esquema:
    """∀ vars. tipo"""
    vars: tuple[str, ...]
    tipo: Tipo


Ambiente = dict[str, Esquema]


def mono(t: Tipo) -> Esquema:
    return Esquema((), t)


def _a() -> TVar:
    return TVar("a")


def _b() -> TVar:
    return TVar("b")


AMBIENTE_PADRAO: Ambiente = {
    "par": Esquema(("a", "b"), seta(_a(), seta(_b(), par(_a(), _b())))),
    "fst": Esquema(("a", "b"), seta(par(_a(), _b()), _a())),
    "snd": Esquema(("a", "b"), seta(par(_a(), _b()), _b())),
    "+": mono(seta(INT, seta(INT, INT))),
    "==": Esquema(("a",), seta(_a(), seta(_a(), BOOL))),
    "fix": Esquema(("a",), seta(seta(_a(), _a()), _a())),
}


def _livres_esquema(e: Esquema) -> set[str]:
    return variaveis(e.tipo) - set(e.vars)


def _livres_amb(env: Ambiente) -> set[str]:
    r: set[str] = set()
    for e in env.values():
        r |= _livres_esquema(e)
    return r


def _aplicar_amb(s: Subst, env: Ambiente) -> Ambiente:
    out: Ambiente = {}
    for k, e in env.items():
        s2 = {v: t for v, t in s.items() if v not in e.vars}
        out[k] = Esquema(e.vars, aplicar(s2, e.tipo))
    return out


def generalizar(env: Ambiente, t: Tipo) -> Esquema:
    return Esquema(tuple(sorted(variaveis(t) - _livres_amb(env))), t)


class _Inferidor:
    def __init__(self) -> None:
        self.n = 0

    def nova(self) -> TVar:
        self.n += 1
        return TVar(f"_t{self.n}")

    def instanciar(self, e: Esquema) -> Tipo:
        return aplicar({v: self.nova() for v in e.vars}, e.tipo)

    def unir(self, a: Tipo, b: Tipo) -> Subst:
        try:
            return unificar(a, b)
        except ErroUnificacao as ex:
            raise ErroTipo(str(ex)) from ex

    def w(self, env: Ambiente, e: Expr) -> tuple[Subst, Tipo]:
        if isinstance(e, EVar):
            if e.nome not in env:
                raise ErroTipo(f"variável não ligada: {e.nome}")
            return {}, self.instanciar(env[e.nome])
        if isinstance(e, ELit):
            return {}, BOOL if isinstance(e.valor, bool) else INT
        if isinstance(e, ELam):
            b = self.nova()
            s1, t1 = self.w({**env, e.param: mono(b)}, e.corpo)
            return s1, seta(aplicar(s1, b), t1)
        if isinstance(e, EApp):
            s1, t1 = self.w(env, e.fun)
            s2, t2 = self.w(_aplicar_amb(s1, env), e.arg)
            b = self.nova()
            s3 = self.unir(aplicar(s2, t1), seta(t2, b))
            return compor(s3, compor(s2, s1)), aplicar(s3, b)
        if isinstance(e, ELet):
            s1, t1 = self.w(env, e.valor)
            env1 = _aplicar_amb(s1, env)
            s2, t2 = self.w({**env1, e.nome: generalizar(env1, t1)}, e.corpo)
            return compor(s2, s1), t2
        s0, tc = self.w(env, e.cond)
        s0 = compor(self.unir(tc, BOOL), s0)
        env = _aplicar_amb(s0, env)
        s1, t1 = self.w(env, e.entao)
        env = _aplicar_amb(s1, env)
        s2, t2 = self.w(env, e.senao)
        s3 = self.unir(aplicar(s2, t1), t2)
        return compor(s3, compor(s2, compor(s1, s0))), aplicar(s3, t2)


def inferir(e: Expr, env: Ambiente | None = None) -> Tipo:
    """Tipo principal de e, com variáveis nomeadas a, b, c..."""
    ambiente = AMBIENTE_PADRAO if env is None else env
    s, t = _Inferidor().w(ambiente, e)
    return normalizar_variaveis(aplicar(s, t))


def esquema_de(e: Expr, env: Ambiente | None = None) -> Esquema:
    t = inferir(e, env)
    return Esquema(tuple(sorted(variaveis(t))), t)


def lam(params: str, corpo: Expr) -> Expr:
    """Açúcar: lam("x y", e) = \\x.\\y.e"""
    for p in reversed(params.split()):
        corpo = ELam(p, corpo)
    return corpo


def app(f: Expr, *args: Expr) -> Expr:
    for a in args:
        f = EApp(f, a)
    return f
