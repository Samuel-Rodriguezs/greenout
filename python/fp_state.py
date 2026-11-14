"""Mônada State: computações com estado passado explicitamente."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Tuple


@dataclass(frozen=True)
class State:
    rodar: Callable[[Any], Tuple[Any, Any]]

    def executar(self, estado: Any) -> Tuple[Any, Any]:
        """Retorna (valor, estado_final)."""
        return self.rodar(estado)

    def avaliar(self, estado: Any) -> Any:
        return self.rodar(estado)[0]

    def estado_final(self, estado: Any) -> Any:
        return self.rodar(estado)[1]

    def map(self, f: Callable[[Any], Any]) -> "State":
        def run(s):
            a, s2 = self.rodar(s)
            return f(a), s2
        return State(run)

    def bind(self, f: Callable[[Any], "State"]) -> "State":
        def run(s):
            a, s2 = self.rodar(s)
            return f(a).rodar(s2)
        return State(run)

    def ap(self, outro: "State") -> "State":
        return self.bind(lambda f: outro.map(f))


def unit(valor: Any) -> State:
    return State(lambda s: (valor, s))


def get() -> State:
    return State(lambda s: (s, s))


def put(novo: Any) -> State:
    return State(lambda s: (None, novo))


def modify(f: Callable[[Any], Any]) -> State:
    return State(lambda s: (None, f(s)))


def gets(f: Callable[[Any], Any]) -> State:
    return State(lambda s: (f(s), s))


def mapear_m(f: Callable[[Any], State], itens: Iterable[Any]) -> State:
    itens = list(itens)

    def run(s):
        saida = []
        for x in itens:
            y, s = f(x).rodar(s)
            saida.append(y)
        return saida, s
    return State(run)


def sequence(ss: Iterable[State]) -> State:
    return mapear_m(lambda m: m, ss)


# Exemplos clássicos -------------------------------------------------------

def rotular(arvore: Any) -> State:
    """Numera as folhas de uma árvore (tuplas aninhadas) em ordem."""
    if isinstance(arvore, tuple):
        esq, dir_ = arvore
        return rotular(esq).bind(
            lambda e: rotular(dir_).map(lambda d: (e, d))
        )
    return get().bind(lambda n: put(n + 1).map(lambda _: (n, arvore)))


def empilhar(x: Any) -> State:
    return modify(lambda pilha: (x,) + pilha)


def desempilhar() -> State:
    def run(pilha):
        if not pilha:
            raise IndexError("pilha vazia")
        return pilha[0], pilha[1:]
    return State(run)
