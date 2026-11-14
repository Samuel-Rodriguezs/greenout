"""Trampolim: recursão (inclusive mútua) sem estourar a pilha."""
from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable


@dataclass(frozen=True)
class Salto:
    """Chamada adiada: executar fn(*args) no próximo passo do trampolim."""

    fn: Callable[..., Any]
    args: tuple = ()


def saltar(fn: Callable[..., Any], *args: Any) -> Salto:
    return Salto(fn, args)


def trampolim(fn: Callable[..., Any], *args: Any) -> Any:
    """Avalia fn(*args), repetindo enquanto o resultado for um Salto."""
    r = fn(*args)
    while isinstance(r, Salto):
        r = r.fn(*r.args)
    return r


def recursiva(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador: a função devolve `saltar(...)` na cauda; a chamada externa resolve."""

    @wraps(fn)
    def envoltorio(*args: Any) -> Any:
        return trampolim(fn, *args)

    return envoltorio


# --- exemplos ---------------------------------------------------------------

def _soma_cauda(n: int, acc: int) -> Any:
    return acc if n == 0 else saltar(_soma_cauda, n - 1, acc + n)


def soma_ate(n: int) -> int:
    return trampolim(_soma_cauda, n, 0)


def _fat(n: int, acc: int) -> Any:
    return acc if n <= 1 else saltar(_fat, n - 1, acc * n)


def fatorial(n: int) -> int:
    return trampolim(_fat, n, 1)


def _par(n: int) -> Any:
    return True if n == 0 else saltar(_impar, n - 1)


def _impar(n: int) -> Any:
    return False if n == 0 else saltar(_par, n - 1)


def eh_par(n: int) -> bool:
    return trampolim(_par, n)


def _mdc(a: int, b: int) -> Any:
    return a if b == 0 else saltar(_mdc, b, a % b)


def mdc(a: int, b: int) -> int:
    return trampolim(_mdc, abs(a), abs(b))
