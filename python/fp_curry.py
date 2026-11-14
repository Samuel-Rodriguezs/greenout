"""Curry, uncurry e aplicação parcial (com marcador de posição)."""
from __future__ import annotations

import inspect
from typing import Any, Callable, Optional


def _aridade(f: Callable[..., Any]) -> int:
    n = 0
    for p in inspect.signature(f).parameters.values():
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
            if p.default is p.empty:
                n += 1
        elif p.kind is p.VAR_POSITIONAL:
            raise ValueError("informe a aridade para funções com *args")
    return n


def curry(f: Callable[..., Any], aridade: Optional[int] = None) -> Callable[..., Any]:
    """Currifica f; cada chamada pode passar um ou mais argumentos."""
    n = _aridade(f) if aridade is None else aridade
    if n < 0:
        raise ValueError("aridade negativa")

    def acumular(recebidos: tuple) -> Callable[..., Any]:
        def passo(*novos: Any) -> Any:
            todos = recebidos + novos
            if len(todos) >= n:
                return f(*todos)
            return acumular(todos)
        return passo

    if n == 0:
        return lambda *a: f(*a)
    return acumular(())


def uncurry(f: Callable[..., Any]) -> Callable[..., Any]:
    """Transforma f currificada (a -> b -> c) em função de argumentos múltiplos."""
    def descurrificada(*args: Any) -> Any:
        r = f
        for a in args:
            r = r(a)
        return r
    return descurrificada


def uncurry_tupla(f: Callable[..., Any]) -> Callable[[tuple], Any]:
    return lambda t: f(*t)


def curry_tupla(f: Callable[[tuple], Any]) -> Callable[..., Any]:
    return lambda *args: f(args)


def flip(f: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
    return lambda a, b: f(b, a)


class _Marcador:
    def __repr__(self) -> str:
        return "_"


_ = _Marcador()


def parcial(f: Callable[..., Any], *fixos: Any, **kw_fixos: Any) -> Callable[..., Any]:
    """Aplicação parcial; `_` marca posições a preencher com os argumentos da chamada."""
    def chamada(*novos: Any, **kw_novos: Any) -> Any:
        fila = list(novos)
        args = []
        for a in fixos:
            if a is _:
                if not fila:
                    raise TypeError("faltam argumentos para os marcadores")
                args.append(fila.pop(0))
            else:
                args.append(a)
        args.extend(fila)
        return f(*args, **{**kw_fixos, **kw_novos})
    return chamada


def aplicar_n(f: Callable[[Any], Any], n: int) -> Callable[[Any], Any]:
    """f composta consigo mesma n vezes."""
    if n < 0:
        raise ValueError("n deve ser >= 0")

    def g(x: Any) -> Any:
        for _i in range(n):
            x = f(x)
        return x
    return g
