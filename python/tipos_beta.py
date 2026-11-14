"""Redução beta: ordem normal (mais externo à esquerda) e aplicativa
(mais interno à esquerda)."""
from __future__ import annotations

from tipos_termos import Abs, App, Termo, Var, substituir


class LimiteExcedido(Exception):
    """A normalização não terminou dentro do limite de passos."""


def passo_normal(t: Termo) -> Termo | None:
    """Um passo de redução em ordem normal; None se já está em forma normal."""
    if isinstance(t, Var):
        return None
    if isinstance(t, Abs):
        r = passo_normal(t.corpo)
        return None if r is None else Abs(t.param, r)
    if isinstance(t.fun, Abs):
        return substituir(t.fun.corpo, t.fun.param, t.arg)
    r = passo_normal(t.fun)
    if r is not None:
        return App(r, t.arg)
    r = passo_normal(t.arg)
    return None if r is None else App(t.fun, r)


def passo_aplicativo(t: Termo) -> Termo | None:
    """Um passo em ordem aplicativa: argumentos são reduzidos antes do redex."""
    if isinstance(t, Var):
        return None
    if isinstance(t, Abs):
        r = passo_aplicativo(t.corpo)
        return None if r is None else Abs(t.param, r)
    r = passo_aplicativo(t.fun)
    if r is not None:
        return App(r, t.arg)
    r = passo_aplicativo(t.arg)
    if r is not None:
        return App(t.fun, r)
    if isinstance(t.fun, Abs):
        return substituir(t.fun.corpo, t.fun.param, t.arg)
    return None


def e_forma_normal(t: Termo) -> bool:
    return passo_normal(t) is None


def normalizar(t: Termo, estrategia: str = "normal", limite: int = 100_000) -> Termo:
    passo = {"normal": passo_normal, "aplicativa": passo_aplicativo}.get(estrategia)
    if passo is None:
        raise ValueError(f"estratégia desconhecida: {estrategia}")
    for _ in range(limite):
        r = passo(t)
        if r is None:
            return t
        t = r
    raise LimiteExcedido(f"mais de {limite} passos")


def contar_passos(t: Termo, estrategia: str = "normal", limite: int = 100_000) -> int:
    passo = passo_normal if estrategia == "normal" else passo_aplicativo
    n = 0
    while (r := passo(t)) is not None:
        t = r
        n += 1
        if n > limite:
            raise LimiteExcedido(f"mais de {limite} passos")
    return n
