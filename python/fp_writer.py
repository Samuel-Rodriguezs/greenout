"""Mônada Writer: computações que acumulam um log (monoide de tuplas)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Tuple


@dataclass(frozen=True)
class Writer:
    valor: Any
    log: Tuple[Any, ...] = ()

    def map(self, f: Callable[[Any], Any]) -> "Writer":
        return Writer(f(self.valor), self.log)

    def bind(self, f: Callable[[Any], "Writer"]) -> "Writer":
        w = f(self.valor)
        return Writer(w.valor, self.log + w.log)

    def ap(self, outro: "Writer") -> "Writer":
        return Writer(self.valor(outro.valor), self.log + outro.log)

    def executar(self) -> Tuple[Any, Tuple[Any, ...]]:
        return self.valor, self.log


def unit(valor: Any) -> Writer:
    return Writer(valor)


def tell(*mensagens: Any) -> Writer:
    return Writer(None, tuple(mensagens))


def censurar(w: Writer, f: Callable[[Tuple[Any, ...]], Iterable[Any]]) -> Writer:
    return Writer(w.valor, tuple(f(w.log)))


def ouvir(w: Writer) -> Writer:
    """Expõe o log como parte do valor: (valor, log)."""
    return Writer((w.valor, w.log), w.log)


def mapear_m(f: Callable[[Any], Writer], itens: Iterable[Any]) -> Writer:
    acc = unit([])
    for x in itens:
        acc = acc.bind(lambda xs, x=x: f(x).map(lambda y: xs + [y]))
    return acc


def fatorial(n: int) -> Writer:
    """Fatorial registrando cada passo."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    if n == 0:
        return tell("fatorial(0) = 1").map(lambda _: 1)
    return fatorial(n - 1).bind(
        lambda r: tell(f"fatorial({n}) = {n} * {r}").map(lambda _: n * r)
    )


def collatz(n: int) -> Writer:
    """Sequência de Collatz no log; valor = número de passos."""
    w = tell(n).map(lambda _: 0)
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        w = w.bind(lambda passos, n=n: tell(n).map(lambda _: passos + 1))
    return w
