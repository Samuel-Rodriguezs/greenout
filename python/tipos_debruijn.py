"""Índices de De Bruijn: conversão, deslocamento, substituição e redução beta."""
from __future__ import annotations

from dataclasses import dataclass

from tipos_beta import LimiteExcedido
from tipos_termos import Abs, App, Termo, Var, livres, nome_fresco


@dataclass(frozen=True)
class Idx:
    n: int


@dataclass(frozen=True)
class Lam:
    corpo: "DB"


@dataclass(frozen=True)
class Ap:
    f: "DB"
    a: "DB"


DB = Idx | Lam | Ap


def para_debruijn(t: Termo, contexto: tuple[str, ...] | None = None) -> DB:
    """Converte para índices. Variáveis livres são resolvidas por `contexto`
    (o primeiro nome tem o menor índice livre); por omissão, a ordem
    alfabética das livres."""
    if contexto is None:
        contexto = tuple(sorted(livres(t)))
    faltam = livres(t) - set(contexto)
    if faltam:
        raise ValueError(f"variáveis livres fora do contexto: {sorted(faltam)}")

    def go(t: Termo, lig: tuple[str, ...]) -> DB:
        if isinstance(t, Var):
            if t.nome in lig:
                return Idx(lig.index(t.nome))
            return Idx(len(lig) + contexto.index(t.nome))
        if isinstance(t, Abs):
            return Lam(go(t.corpo, (t.param,) + lig))
        return Ap(go(t.fun, lig), go(t.arg, lig))

    return go(t, ())


def de_debruijn(d: DB, contexto: tuple[str, ...] = ()) -> Termo:
    """Volta para nomes; binders recebem a, b, c... evitando as livres."""
    usados = set(contexto)

    def go(d: DB, lig: tuple[str, ...]) -> Termo:
        if isinstance(d, Idx):
            if d.n < len(lig):
                return Var(lig[d.n])
            k = d.n - len(lig)
            if k >= len(contexto):
                raise ValueError(f"índice livre sem nome: {d.n}")
            return Var(contexto[k])
        if isinstance(d, Lam):
            nome = nome_fresco("x", usados | set(lig))
            return Abs(nome, go(d.corpo, (nome,) + lig))
        return App(go(d.f, lig), go(d.a, lig))

    return go(d, ())


def desloca(d: int, c: int, t: DB) -> DB:
    """Soma d aos índices livres (>= c)."""
    if isinstance(t, Idx):
        if t.n < c:
            return t
        if t.n + d < 0:
            raise ValueError("deslocamento negativo inválido")
        return Idx(t.n + d)
    if isinstance(t, Lam):
        return Lam(desloca(d, c + 1, t.corpo))
    return Ap(desloca(d, c, t.f), desloca(d, c, t.a))


def substituir(j: int, s: DB, t: DB) -> DB:
    """t[j := s]."""
    if isinstance(t, Idx):
        return s if t.n == j else t
    if isinstance(t, Lam):
        return Lam(substituir(j + 1, desloca(1, 0, s), t.corpo))
    return Ap(substituir(j, s, t.f), substituir(j, s, t.a))


def beta(corpo: DB, arg: DB) -> DB:
    """Contrai (λ.corpo) arg."""
    return desloca(-1, 0, substituir(0, desloca(1, 0, arg), corpo))


def passo(t: DB) -> DB | None:
    """Um passo em ordem normal."""
    if isinstance(t, Idx):
        return None
    if isinstance(t, Lam):
        r = passo(t.corpo)
        return None if r is None else Lam(r)
    if isinstance(t.f, Lam):
        return beta(t.f.corpo, t.a)
    r = passo(t.f)
    if r is not None:
        return Ap(r, t.a)
    r = passo(t.a)
    return None if r is None else Ap(t.f, r)


def normalizar(t: DB, limite: int = 100_000) -> DB:
    for _ in range(limite):
        r = passo(t)
        if r is None:
            return t
        t = r
    raise LimiteExcedido(f"mais de {limite} passos")


def mostrar(t: DB) -> str:
    if isinstance(t, Idx):
        return str(t.n)
    if isinstance(t, Lam):
        return f"λ {mostrar(t.corpo)}"
    f = mostrar(t.f)
    if isinstance(t.f, Lam):
        f = f"({f})"
    a = mostrar(t.a)
    if not isinstance(t.a, Idx):
        a = f"({a})"
    return f"{f} {a}"
