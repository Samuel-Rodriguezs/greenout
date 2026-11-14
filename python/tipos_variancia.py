"""Variância (co, contra, invariância, bivariância) de construtores de tipo:
subtipagem de tipos parametrizados, inferência e verificação de anotações."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Var(Enum):
    CO = "+"
    CONTRA = "-"
    INV = "="
    BI = "o"  # parâmetro não usado: qualquer coisa serve


@dataclass(frozen=True)
class TP:
    """Parâmetro de tipo (variável)."""
    nome: str


@dataclass(frozen=True)
class TB:
    """Tipo base."""
    nome: str


@dataclass(frozen=True)
class TA:
    """Construtor aplicado."""
    ctor: str
    args: tuple["Tipo", ...] = ()


Tipo = TP | TB | TA
Tabela = dict[str, tuple[Var, ...]]


def fn(a: Tipo, b: Tipo) -> TA:
    return TA("->", (a, b))


def tabela_padrao() -> Tabela:
    return {
        "->": (Var.CONTRA, Var.CO),
        "Lista": (Var.CO,),
        "Par": (Var.CO, Var.CO),
        "Escritor": (Var.CONTRA,),   # consome valores (sink)
        "Ref": (Var.INV,),           # lê e escreve
        "Constante": (Var.BI,),      # ignora o parâmetro (tipo fantasma)
    }


def inverter(v: Var) -> Var:
    return {Var.CO: Var.CONTRA, Var.CONTRA: Var.CO}.get(v, v)


def compor(externa: Var, interna: Var) -> Var:
    """Variância de um parâmetro dentro de um construtor, dentro de outro."""
    if Var.BI in (externa, interna):
        return Var.BI
    if Var.INV in (externa, interna):
        return Var.INV
    return Var.CO if externa == interna else Var.CONTRA


def combinar(a: Var, b: Var) -> Var:
    """Junta dois usos do mesmo parâmetro."""
    if a == Var.BI:
        return b
    if b == Var.BI:
        return a
    return a if a == b else Var.INV


def variancia_em(t: Tipo, param: str, tabela: Tabela) -> Var:
    """Posição de `param` em t: CO se só em posições positivas, etc."""
    if isinstance(t, TP):
        return Var.CO if t.nome == param else Var.BI
    if isinstance(t, TB):
        return Var.BI
    if t.ctor not in tabela:
        raise KeyError(f"construtor sem variância declarada: {t.ctor}")
    vs = tabela[t.ctor]
    if len(vs) != len(t.args):
        raise ValueError(f"aridade de {t.ctor}: esperado {len(vs)}, obtido {len(t.args)}")
    r = Var.BI
    for v, a in zip(vs, t.args):
        r = combinar(r, compor(v, variancia_em(a, param, tabela)))
    return r


def inferir_variancias(params: tuple[str, ...], corpo: Tipo, tabela: Tabela) -> tuple[Var, ...]:
    return tuple(variancia_em(corpo, p, tabela) for p in params)


def declarar(tabela: Tabela, nome: str, params: tuple[str, ...], corpo: Tipo,
             anotadas: tuple[Var, ...] | None = None) -> tuple[Var, ...]:
    """Registra o construtor `nome`; verifica anotações contra a inferência."""
    inferidas = inferir_variancias(params, corpo, tabela)
    if anotadas is None:
        tabela[nome] = inferidas
        return inferidas
    if len(anotadas) != len(params):
        raise ValueError("número de anotações difere do número de parâmetros")
    for p, anot, inf in zip(params, anotadas, inferidas):
        permitido = {
            Var.INV: set(Var),
            Var.CO: {Var.CO, Var.BI},
            Var.CONTRA: {Var.CONTRA, Var.BI},
            Var.BI: {Var.BI},
        }[anot]
        if inf not in permitido:
            raise TypeError(f"parâmetro {p} anotado {anot.value} mas usado como {inf.value}")
    tabela[nome] = anotadas
    return anotadas


def subtipo(a: Tipo, b: Tipo, tabela: Tabela,
            bases: set[tuple[str, str]] | None = None) -> bool:
    """a <: b. `bases` lista pares (sub, super) já fechados transitivamente."""
    bases = bases or set()
    if isinstance(a, TP) or isinstance(b, TP):
        return a == b
    if isinstance(a, TB) and isinstance(b, TB):
        return a == b or (a.nome, b.nome) in bases
    if isinstance(a, TA) and isinstance(b, TA):
        if a.ctor != b.ctor or len(a.args) != len(b.args):
            return False
        vs = tabela[a.ctor]
        for v, x, y in zip(vs, a.args, b.args):
            if v == Var.CO and not subtipo(x, y, tabela, bases):
                return False
            if v == Var.CONTRA and not subtipo(y, x, tabela, bases):
                return False
            if v == Var.INV and not (subtipo(x, y, tabela, bases) and subtipo(y, x, tabela, bases)):
                return False
        return True
    return False


def mostrar(t: Tipo) -> str:
    if isinstance(t, (TP, TB)):
        return t.nome
    if t.ctor == "->":
        a, b = t.args
        esq = mostrar(a)
        return f"({esq}) -> {mostrar(b)}" if isinstance(a, TA) and a.ctor == "->" else f"{esq} -> {mostrar(b)}"
    return f"{t.ctor}[{', '.join(mostrar(a) for a in t.args)}]" if t.args else t.ctor
