"""Combinadores SKI: redução e tradução de cálculo lambda para SKI
(abstração de colchetes)."""
from __future__ import annotations

from dataclasses import dataclass

from tipos_beta import LimiteExcedido
from tipos_termos import Abs, App, Termo, Var, livres


@dataclass(frozen=True)
class Atomo:
    nome: str  # "S", "K", "I" ou uma variável livre


@dataclass(frozen=True)
class Ap:
    f: "SKI"
    a: "SKI"


SKI = Atomo | Ap
S, K, I = Atomo("S"), Atomo("K"), Atomo("I")
_RESERVADOS = {"S", "K", "I"}


def aplicar(f: SKI, *args: SKI) -> SKI:
    for a in args:
        f = Ap(f, a)
    return f


def _tem(x: str, t: SKI) -> bool:
    if isinstance(t, Atomo):
        return t.nome == x
    return _tem(x, t.f) or _tem(x, t.a)


def _abstrair(x: str, t: SKI) -> SKI:
    """[x] t, sem usar eta para manter a tradução previsível."""
    if not _tem(x, t):
        return Ap(K, t)
    if isinstance(t, Atomo):
        return I  # t == x
    return aplicar(S, _abstrair(x, t.f), _abstrair(x, t.a))


def de_lambda(t: Termo) -> SKI:
    """Traduz um termo lambda para SKI; variáveis livres viram átomos."""
    if isinstance(t, Var):
        if t.nome in _RESERVADOS:
            raise ValueError(f"nome reservado: {t.nome}")
        return Atomo(t.nome)
    if isinstance(t, App):
        return Ap(de_lambda(t.fun), de_lambda(t.arg))
    if t.param in _RESERVADOS:
        raise ValueError(f"nome reservado: {t.param}")
    return _abstrair(t.param, de_lambda(t.corpo))


def espinha(t: SKI) -> tuple[SKI, list[SKI]]:
    args: list[SKI] = []
    while isinstance(t, Ap):
        args.append(t.a)
        t = t.f
    args.reverse()
    return t, args


def passo(t: SKI) -> SKI | None:
    """Um passo de redução em ordem normal; None se for forma normal."""
    cab, args = espinha(t)
    if cab == I and len(args) >= 1:
        return aplicar(args[0], *args[1:])
    if cab == K and len(args) >= 2:
        return aplicar(args[0], *args[2:])
    if cab == S and len(args) >= 3:
        x, y, z = args[:3]
        return aplicar(x, z, Ap(y, z), *args[3:])
    for i, a in enumerate(args):
        r = passo(a)
        if r is not None:
            return aplicar(cab, *args[:i], r, *args[i + 1:])
    return None


def normalizar(t: SKI, limite: int = 100_000) -> SKI:
    for _ in range(limite):
        r = passo(t)
        if r is None:
            return t
        t = r
    raise LimiteExcedido(f"mais de {limite} passos")


def mostrar(t: SKI) -> str:
    if isinstance(t, Atomo):
        return t.nome
    a = mostrar(t.a)
    return f"{mostrar(t.f)} {'(' + a + ')' if isinstance(t.a, Ap) else a}"


def tamanho(t: SKI) -> int:
    return 1 if isinstance(t, Atomo) else tamanho(t.f) + tamanho(t.a)
