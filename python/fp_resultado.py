"""Mônada Either/Result: Ok e Err com map, bind e captura de exceções."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Tuple, Type, Union


@dataclass(frozen=True)
class Ok:
    valor: Any

    def map(self, f: Callable[[Any], Any]) -> "Resultado":
        return Ok(f(self.valor))

    def map_err(self, f: Callable[[Any], Any]) -> "Resultado":
        return self

    def bind(self, f: Callable[[Any], "Resultado"]) -> "Resultado":
        return f(self.valor)

    def ap(self, outro: "Resultado") -> "Resultado":
        return outro.map(self.valor)

    def get_or(self, padrao: Any) -> Any:
        return self.valor

    def eh_ok(self) -> bool:
        return True

    def dobrar(self, f_err: Callable, f_ok: Callable) -> Any:
        return f_ok(self.valor)


@dataclass(frozen=True)
class Err:
    erro: Any

    def map(self, f: Callable[[Any], Any]) -> "Resultado":
        return self

    def map_err(self, f: Callable[[Any], Any]) -> "Resultado":
        return Err(f(self.erro))

    def bind(self, f: Callable[[Any], "Resultado"]) -> "Resultado":
        return self

    def ap(self, outro: "Resultado") -> "Resultado":
        return self

    def get_or(self, padrao: Any) -> Any:
        return padrao

    def eh_ok(self) -> bool:
        return False

    def dobrar(self, f_err: Callable, f_ok: Callable) -> Any:
        return f_err(self.erro)


Resultado = Union[Ok, Err]


def unit(valor: Any) -> Resultado:
    return Ok(valor)


def tentar(f: Callable[..., Any], *args: Any,
           excecoes: Tuple[Type[BaseException], ...] = (Exception,)) -> Resultado:
    """Executa f capturando exceções como Err(exceção)."""
    try:
        return Ok(f(*args))
    except excecoes as e:
        return Err(e)


def sequence(rs: Iterable[Resultado]) -> Resultado:
    """Curto-circuita no primeiro Err."""
    valores = []
    for r in rs:
        if isinstance(r, Err):
            return r
        valores.append(r.valor)
    return Ok(valores)


def traverse(f: Callable[[Any], Resultado], itens: Iterable[Any]) -> Resultado:
    return sequence(f(x) for x in itens)


def particionar(rs: Iterable[Resultado]) -> Tuple[list, list]:
    oks, errs = [], []
    for r in rs:
        if isinstance(r, Ok):
            oks.append(r.valor)
        else:
            errs.append(r.erro)
    return oks, errs


def recuperar(r: Resultado, f: Callable[[Any], Resultado]) -> Resultado:
    return f(r.erro) if isinstance(r, Err) else r
