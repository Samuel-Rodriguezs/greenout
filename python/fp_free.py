"""Mônada Free sobre um DSL de armazenamento, com interpretadores intercambiáveis."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, List, Tuple, Union


@dataclass(frozen=True)
class Pure:
    valor: Any

    def bind(self, f: Callable[[Any], "Programa"]) -> "Programa":
        return f(self.valor)

    def map(self, f: Callable[[Any], Any]) -> "Programa":
        return Pure(f(self.valor))


@dataclass(frozen=True)
class Free:
    instrucao: Any  # functor: possui fmap

    def bind(self, f: Callable[[Any], "Programa"]) -> "Programa":
        return Free(self.instrucao.fmap(lambda m: m.bind(f)))

    def map(self, f: Callable[[Any], Any]) -> "Programa":
        return self.bind(lambda a: Pure(f(a)))


Programa = Union[Pure, Free]


# Instruções: cada uma guarda a continuação k (resultado -> Programa) ------------

@dataclass(frozen=True)
class Ler:
    chave: str
    k: Callable[[Any], Programa]

    def fmap(self, f: Callable) -> "Ler":
        return replace(self, k=lambda x: f(self.k(x)))


@dataclass(frozen=True)
class Escrever:
    chave: str
    valor: Any
    k: Callable[[Any], Programa]

    def fmap(self, f: Callable) -> "Escrever":
        return replace(self, k=lambda x: f(self.k(x)))


@dataclass(frozen=True)
class Logar:
    mensagem: str
    k: Callable[[Any], Programa]

    def fmap(self, f: Callable) -> "Logar":
        return replace(self, k=lambda x: f(self.k(x)))


def unit(valor: Any) -> Programa:
    return Pure(valor)


def ler(chave: str) -> Programa:
    return Free(Ler(chave, Pure))


def escrever(chave: str, valor: Any) -> Programa:
    return Free(Escrever(chave, valor, Pure))


def logar(mensagem: str) -> Programa:
    return Free(Logar(mensagem, Pure))


def sequence(programas: List[Programa]) -> Programa:
    prog: Programa = Pure([])
    for p in programas:
        prog = prog.bind(lambda xs, p=p: p.map(lambda x: xs + [x]))
    return prog


# Interpretação ---------------------------------------------------------------------

def interpretar(prog: Programa, tratar: Callable[[Any], Any]) -> Any:
    """Consome o programa instrução a instrução (iterativo, sem recursão)."""
    while isinstance(prog, Free):
        i = prog.instrucao
        prog = i.k(tratar(i))
    return prog.valor


def executar_puro(prog: Programa, estado: Dict[str, Any]) -> Tuple[Any, Dict[str, Any], List[str]]:
    """Interpretador puro: devolve (resultado, novo_estado, logs) sem mutar `estado`."""
    mem = dict(estado)
    logs: List[str] = []

    def tratar(i: Any) -> Any:
        if isinstance(i, Ler):
            return mem.get(i.chave)
        if isinstance(i, Escrever):
            mem[i.chave] = i.valor
            return None
        if isinstance(i, Logar):
            logs.append(i.mensagem)
            return None
        raise TypeError(f"instrução desconhecida: {i!r}")

    return interpretar(prog, tratar), mem, logs


def rastrear(prog: Programa, leituras: Dict[str, Any]) -> List[str]:
    """Interpretador alternativo: apenas descreve as instruções, sem efeitos."""
    trilha: List[str] = []

    def tratar(i: Any) -> Any:
        if isinstance(i, Ler):
            trilha.append(f"ler {i.chave}")
            return leituras.get(i.chave)
        if isinstance(i, Escrever):
            trilha.append(f"escrever {i.chave}={i.valor!r}")
        elif isinstance(i, Logar):
            trilha.append(f"logar {i.mensagem}")
        return None

    interpretar(prog, tratar)
    return trilha


def incrementar(chave: str) -> Programa:
    """Exemplo: lê, soma 1, grava e registra."""
    return (
        ler(chave)
        .map(lambda v: (v or 0) + 1)
        .bind(lambda novo: escrever(chave, novo).bind(
            lambda _: logar(f"{chave} -> {novo}").map(lambda _: novo)))
    )
