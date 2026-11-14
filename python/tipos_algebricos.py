"""Tipos algébricos (soma e produto), valores, tipagem de padrões e
eliminação por pattern matching."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from tipos_unificacao import BOOL, INT, TCon, TVar, Tipo, aplicar, lista, mostrar


class ErroTipo(Exception):
    pass


@dataclass(frozen=True)
class Con:
    """Valor construído: construtor aplicado a argumentos."""
    nome: str
    args: tuple["Valor", ...] = ()


Valor = Con | int | bool


@dataclass(frozen=True)
class PVar:
    nome: str


@dataclass(frozen=True)
class PCoringa:
    pass


@dataclass(frozen=True)
class PLit:
    valor: int | bool


@dataclass(frozen=True)
class PCon:
    nome: str
    subs: tuple["Padrao", ...] = ()


Padrao = PVar | PCoringa | PLit | PCon


@dataclass(frozen=True)
class DefTipo:
    nome: str
    params: tuple[str, ...]
    construtores: tuple[tuple[str, tuple[Tipo, ...]], ...]

    def campos(self, construtor: str) -> tuple[Tipo, ...]:
        for n, c in self.construtores:
            if n == construtor:
                return c
        raise KeyError(construtor)


class Universo:
    """Conjunto de declarações de tipos de dados."""

    def __init__(self) -> None:
        self.tipos: dict[str, DefTipo] = {}
        self.por_construtor: dict[str, DefTipo] = {}

    def declarar(self, nome: str, params: tuple[str, ...],
                 construtores: dict[str, tuple[Tipo, ...]]) -> DefTipo:
        if nome in self.tipos:
            raise ErroTipo(f"tipo já declarado: {nome}")
        if not construtores:
            raise ErroTipo(f"tipo {nome} sem construtores")
        for c, campos in construtores.items():
            if c in self.por_construtor:
                raise ErroTipo(f"construtor já declarado: {c}")
            livres = {v for t in campos for v in _vars(t)}
            if livres - set(params):
                raise ErroTipo(f"variável de tipo livre em {c}")
        d = DefTipo(nome, params, tuple(construtores.items()))
        self.tipos[nome] = d
        for c in construtores:
            self.por_construtor[c] = d
        return d

    def definicao_de(self, construtor: str) -> DefTipo:
        if construtor not in self.por_construtor:
            raise ErroTipo(f"construtor desconhecido: {construtor}")
        return self.por_construtor[construtor]

    def campos_instanciados(self, construtor: str, t: Tipo) -> tuple[Tipo, ...]:
        """Tipos dos campos de `construtor` quando o resultado tem o tipo t."""
        d = self.definicao_de(construtor)
        if not (isinstance(t, TCon) and t.nome == d.nome and len(t.args) == len(d.params)):
            raise ErroTipo(f"construtor {construtor} não pertence a {mostrar(t)}")
        s = dict(zip(d.params, t.args))
        return tuple(aplicar(s, c) for c in d.campos(construtor))


def _vars(t: Tipo) -> set[str]:
    if isinstance(t, TVar):
        return {t.nome}
    return {v for a in t.args for v in _vars(a)}


def universo_padrao() -> Universo:
    u = Universo()
    a, b = TVar("a"), TVar("b")
    u.declarar("Opcao", ("a",), {"Nada": (), "Algum": (a,)})
    u.declarar("Ou", ("a", "b"), {"Esq": (a,), "Dir": (b,)})
    u.declarar("Par", ("a", "b"), {"MkPar": (a, b)})
    u.declarar("List", ("a",), {"Nil": (), "Cons": (a, lista(a))})
    return u


def verificar_valor(v: Valor, t: Tipo, u: Universo) -> bool:
    if isinstance(v, bool):
        return t == BOOL
    if isinstance(v, int):
        return t == INT
    try:
        campos = u.campos_instanciados(v.nome, t)
    except ErroTipo:
        return False
    return len(campos) == len(v.args) and all(
        verificar_valor(x, c, u) for x, c in zip(v.args, campos))


def tipar_padrao(p: Padrao, t: Tipo, u: Universo) -> dict[str, Tipo]:
    """Tipos das variáveis ligadas por p ao casar com um valor de tipo t."""
    if isinstance(p, PCoringa):
        return {}
    if isinstance(p, PVar):
        return {p.nome: t}
    if isinstance(p, PLit):
        esperado = BOOL if isinstance(p.valor, bool) else INT
        if t != esperado:
            raise ErroTipo(f"literal {p.valor!r} não tem tipo {mostrar(t)}")
        return {}
    campos = u.campos_instanciados(p.nome, t)
    if len(campos) != len(p.subs):
        raise ErroTipo(f"{p.nome} espera {len(campos)} argumentos, recebeu {len(p.subs)}")
    out: dict[str, Tipo] = {}
    for sub, c in zip(p.subs, campos):
        for k, v in tipar_padrao(sub, c, u).items():
            if k in out:
                raise ErroTipo(f"variável repetida no padrão: {k}")
            out[k] = v
    return out


def casar(p: Padrao, v: Valor) -> dict[str, Valor] | None:
    """Ligações se v casa com p; None caso contrário."""
    if isinstance(p, PCoringa):
        return {}
    if isinstance(p, PVar):
        return {p.nome: v}
    if isinstance(p, PLit):
        ok = isinstance(v, bool) == isinstance(p.valor, bool) and v == p.valor
        return {} if ok else None
    if not isinstance(v, Con) or v.nome != p.nome or len(v.args) != len(p.subs):
        return None
    out: dict[str, Valor] = {}
    for sub, x in zip(p.subs, v.args):
        r = casar(sub, x)
        if r is None:
            return None
        out.update(r)
    return out


def escolher(v: Valor, ramos: list[tuple[Padrao, Callable[[dict[str, Valor]], Any]]]) -> Any:
    """Executa o primeiro ramo cujo padrão casa; MatchError se nenhum."""
    for p, corpo in ramos:
        r = casar(p, v)
        if r is not None:
            return corpo(r)
    raise LookupError(f"nenhum padrão casa com {v!r}")


def eliminar(v: Con, casos: dict[str, Callable[..., Any]], u: Universo) -> Any:
    """Eliminador de tipo soma: um caso por construtor (obrigatório e exato)."""
    d = u.definicao_de(v.nome)
    esperados = {c for c, _ in d.construtores}
    if set(casos) != esperados:
        raise ErroTipo(f"casos devem ser exatamente {sorted(esperados)}")
    return casos[v.nome](*v.args)
