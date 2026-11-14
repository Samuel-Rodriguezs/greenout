"""Mônada Reader: computações que dependem de um ambiente somente leitura."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Reader:
    rodar: Callable[[Any], Any]

    def executar(self, ambiente: Any) -> Any:
        return self.rodar(ambiente)

    def map(self, f: Callable[[Any], Any]) -> "Reader":
        return Reader(lambda env: f(self.rodar(env)))

    def bind(self, f: Callable[[Any], "Reader"]) -> "Reader":
        return Reader(lambda env: f(self.rodar(env)).rodar(env))

    def ap(self, outro: "Reader") -> "Reader":
        return Reader(lambda env: self.rodar(env)(outro.rodar(env)))


def unit(valor: Any) -> Reader:
    return Reader(lambda env: valor)


def ask() -> Reader:
    return Reader(lambda env: env)


def asks(f: Callable[[Any], Any]) -> Reader:
    return Reader(f)


def local(f: Callable[[Any], Any], r: Reader) -> Reader:
    """Executa r com o ambiente modificado por f (sem afetar o externo)."""
    return Reader(lambda env: r.rodar(f(env)))


def sequence(rs) -> Reader:
    rs = list(rs)
    return Reader(lambda env: [r.rodar(env) for r in rs])


def saudacao() -> Reader:
    """Exemplo: configuração injetada como ambiente."""
    return asks(lambda c: c["prefixo"]).bind(
        lambda p: asks(lambda c: c["nome"]).map(lambda n: f"{p} {n}")
    )
