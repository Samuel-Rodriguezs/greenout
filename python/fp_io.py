"""Mônada IO simulada: efeitos descritos como valores e só executados em `executar`."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List


@dataclass(frozen=True)
class IO:
    acao: Callable[[], Any]

    def executar(self) -> Any:
        return self.acao()

    def map(self, f: Callable[[Any], Any]) -> "IO":
        return IO(lambda: f(self.acao()))

    def bind(self, f: Callable[[Any], "IO"]) -> "IO":
        return IO(lambda: f(self.acao()).acao())

    def ap(self, outro: "IO") -> "IO":
        return IO(lambda: self.acao()(outro.acao()))

    def depois(self, outro: "IO") -> "IO":
        return self.bind(lambda _: outro)


def unit(valor: Any) -> IO:
    return IO(lambda: valor)


@dataclass
class Console:
    """Mundo simulado: entradas pré-definidas e saídas capturadas."""
    entradas: List[str] = field(default_factory=list)
    saidas: List[str] = field(default_factory=list)
    _pos: int = 0

    def ler(self) -> str:
        if self._pos >= len(self.entradas):
            raise EOFError("sem mais entradas")
        v = self.entradas[self._pos]
        self._pos += 1
        return v

    def escrever(self, texto: str) -> None:
        self.saidas.append(texto)


def ler_linha(console: Console) -> IO:
    return IO(console.ler)


def escrever(console: Console, texto: str) -> IO:
    return IO(lambda: console.escrever(texto))


def sequence(ios: Iterable[IO]) -> IO:
    ios = list(ios)
    return IO(lambda: [m.executar() for m in ios])


def repetir(n: int, io: IO) -> IO:
    return IO(lambda: [io.executar() for _ in range(n)])


def programa_eco(console: Console) -> IO:
    """Lê um nome e escreve uma saudação."""
    return ler_linha(console).bind(lambda nome: escrever(console, f"Olá, {nome}!"))
