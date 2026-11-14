"""Tipos refinados: um tipo base mais um predicado, verificados em tempo de
execução (ex.: {x: int | x > 0}), com combinadores e contratos de funções."""
from __future__ import annotations

import functools
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Iterable


class ErroRefinamento(TypeError):
    pass


class Refinado:
    """{ v : base | predicado(v) }"""

    def __init__(self, nome: str, base: "type | Refinado",
                 predicado: Callable[[Any], bool], descricao: str = "") -> None:
        self.nome = nome
        self.base = base
        self.predicado = predicado
        self.descricao = descricao or nome

    def contem(self, valor: Any) -> bool:
        if isinstance(self.base, Refinado):
            if not self.base.contem(valor):
                return False
        elif not _instancia_exata(valor, self.base):
            return False
        try:
            return bool(self.predicado(valor))
        except Exception:
            return False

    def validar(self, valor: Any) -> Any:
        if not self.contem(valor):
            raise ErroRefinamento(f"{valor!r} não satisfaz {self.nome} ({self.descricao})")
        return valor

    def criar(self, valor: Any) -> "ValorRefinado":
        return ValorRefinado(self, self.validar(valor))

    def __repr__(self) -> str:
        return f"{{{self.nome}}}"

    def __and__(self, outro: "Refinado") -> "Refinado":
        return Refinado(f"{self.nome}&{outro.nome}", object,
                        lambda v: self.contem(v) and outro.contem(v),
                        f"({self.descricao}) e ({outro.descricao})")

    def __or__(self, outro: "Refinado") -> "Refinado":
        return Refinado(f"{self.nome}|{outro.nome}", object,
                        lambda v: self.contem(v) or outro.contem(v),
                        f"({self.descricao}) ou ({outro.descricao})")


def _instancia_exata(valor: Any, tipo: type) -> bool:
    """isinstance, mas bool não conta como int."""
    if tipo is int:
        return isinstance(valor, int) and not isinstance(valor, bool)
    return isinstance(valor, tipo)


@dataclass(frozen=True)
class ValorRefinado:
    tipo: Refinado
    valor: Any

    def mapear(self, f: Callable[[Any], Any], destino: Refinado | None = None) -> "ValorRefinado":
        """Aplica f e revalida: o invariante não é herdado automaticamente."""
        return (destino or self.tipo).criar(f(self.valor))


def refinar(nome: str, base: "type | Refinado", predicado: Callable[[Any], bool],
            descricao: str = "") -> Refinado:
    return Refinado(nome, base, predicado, descricao)


def faixa(minimo: float, maximo: float, base: type = int) -> Refinado:
    return Refinado(f"{base.__name__}[{minimo}..{maximo}]", base,
                    lambda v: minimo <= v <= maximo, f"{minimo} <= v <= {maximo}")


def comprimento(minimo: int, maximo: int | None = None, base: type = str) -> Refinado:
    return Refinado(f"{base.__name__}[len {minimo}..{maximo}]", base,
                    lambda v: len(v) >= minimo and (maximo is None or len(v) <= maximo),
                    f"len entre {minimo} e {maximo if maximo is not None else 'inf'}")


def elementos(tipo_elem: "type | Refinado", base: type = list) -> Refinado:
    def ok(xs: Iterable[Any]) -> bool:
        return all(tipo_elem.contem(x) if isinstance(tipo_elem, Refinado)
                   else _instancia_exata(x, tipo_elem) for x in xs)
    return Refinado(f"{base.__name__}<{getattr(tipo_elem, 'nome', getattr(tipo_elem, '__name__', '?'))}>",
                    base, ok, "todos os elementos válidos")


NATURAL = refinar("Natural", int, lambda v: v >= 0, "v >= 0")
POSITIVO = refinar("Positivo", int, lambda v: v > 0, "v > 0")
NAO_VAZIA = comprimento(1)
PORCENTAGEM = faixa(0, 100)


def implica(a: Refinado, b: Refinado, amostras: Iterable[Any]) -> bool:
    """Teste de subtipagem a <: b sobre amostras: todo valor de a está em b?"""
    return all(b.contem(x) for x in amostras if a.contem(x))


def contrato(_retorno: "Refinado | type | None" = None, /,
             **parametros: "Refinado | type") -> Callable:
    """Decorador que valida argumentos nomeados e o retorno em tempo de execução."""
    def decorador(f: Callable) -> Callable:
        sig = inspect.signature(f)
        for p in parametros:
            if p not in sig.parameters:
                raise TypeError(f"parâmetro inexistente em {f.__name__}: {p}")

        @functools.wraps(f)
        def envolvido(*args: Any, **kw: Any) -> Any:
            ligados = sig.bind(*args, **kw)
            ligados.apply_defaults()
            for nome, tipo in parametros.items():
                _checar(tipo, ligados.arguments[nome], f"{f.__name__}({nome})")
            r = f(*args, **kw)
            if _retorno is not None:
                _checar(_retorno, r, f"{f.__name__} -> retorno")
            return r
        return envolvido
    return decorador


def _checar(tipo: "Refinado | type", valor: Any, onde: str) -> None:
    if isinstance(tipo, Refinado):
        try:
            tipo.validar(valor)
        except ErroRefinamento as e:
            raise ErroRefinamento(f"{onde}: {e}") from None
    elif not _instancia_exata(valor, tipo):
        raise ErroRefinamento(f"{onde}: esperado {tipo.__name__}, obtido {type(valor).__name__}")
