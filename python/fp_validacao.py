"""Applicative Validação: acumula todos os erros em vez de parar no primeiro."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Tuple, Union


@dataclass(frozen=True)
class Valido:
    valor: Any

    def map(self, f: Callable[[Any], Any]) -> "Validacao":
        return Valido(f(self.valor))

    def ap(self, outro: "Validacao") -> "Validacao":
        """self contém uma função; erros de ambos os lados são acumulados."""
        return outro.map(self.valor)

    def entao(self, f: Callable[[Any], "Validacao"]) -> "Validacao":
        return f(self.valor)


@dataclass(frozen=True)
class Invalido:
    erros: Tuple[str, ...]

    def map(self, f: Callable[[Any], Any]) -> "Validacao":
        return self

    def ap(self, outro: "Validacao") -> "Validacao":
        if isinstance(outro, Invalido):
            return Invalido(self.erros + outro.erros)
        return self

    def entao(self, f: Callable[[Any], "Validacao"]) -> "Validacao":
        return self


Validacao = Union[Valido, Invalido]


def unit(valor: Any) -> Validacao:
    return Valido(valor)


def erro(*mensagens: str) -> Validacao:
    return Invalido(tuple(mensagens))


def _curry(f: Callable[..., Any], n: int) -> Any:
    if n == 0:
        return f()
    return lambda x: _curry(lambda *rest: f(x, *rest), n - 1)


def aplicar(f: Callable[..., Any], *validacoes: Validacao) -> Validacao:
    """liftA-n: aplica f aos valores se todos válidos, senão junta os erros."""
    acc: Validacao = Valido(_curry(f, len(validacoes)))
    for v in validacoes:
        acc = acc.ap(v)
    return acc


def sequence(vs: Iterable[Validacao]) -> Validacao:
    vs = list(vs)
    erros: Tuple[str, ...] = ()
    for v in vs:
        if isinstance(v, Invalido):
            erros += v.erros
    return Invalido(erros) if erros else Valido([v.valor for v in vs])


def traverse(f: Callable[[Any], Validacao], itens: Iterable[Any]) -> Validacao:
    return sequence(f(x) for x in itens)


# Exemplo: validação de cadastro ------------------------------------------

def valida_nome(nome: str) -> Validacao:
    return Valido(nome.strip()) if nome.strip() else erro("nome vazio")


def valida_idade(idade: int) -> Validacao:
    if not isinstance(idade, int) or isinstance(idade, bool):
        return erro("idade deve ser inteira")
    return Valido(idade) if 0 <= idade <= 150 else erro("idade fora do intervalo")


def valida_email(email: str) -> Validacao:
    return Valido(email) if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) else erro("email inválido")


def valida_cadastro(nome: str, idade: int, email: str) -> Validacao:
    return aplicar(
        lambda n, i, e: {"nome": n, "idade": i, "email": e},
        valida_nome(nome), valida_idade(idade), valida_email(email),
    )
