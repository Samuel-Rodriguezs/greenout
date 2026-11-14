"""Lista persistente imutável (cons list) com compartilhamento estrutural."""
from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Optional


class Lista:
    """Lista encadeada imutável. `VAZIA` é a lista vazia; `cons` prepende em O(1)."""

    __slots__ = ("_cabeca", "_cauda", "_tam")

    def __init__(self, cabeca: Any = None, cauda: Optional["Lista"] = None):
        if cauda is None:  # construtor da lista vazia
            object.__setattr__(self, "_cabeca", None)
            object.__setattr__(self, "_cauda", None)
            object.__setattr__(self, "_tam", 0)
        else:
            object.__setattr__(self, "_cabeca", cabeca)
            object.__setattr__(self, "_cauda", cauda)
            object.__setattr__(self, "_tam", cauda._tam + 1)

    def __setattr__(self, nome: str, valor: Any) -> None:
        raise AttributeError("Lista é imutável")

    @property
    def vazia(self) -> bool:
        return self._cauda is None

    @property
    def cabeca(self) -> Any:
        if self.vazia:
            raise IndexError("lista vazia")
        return self._cabeca

    @property
    def cauda(self) -> "Lista":
        if self.vazia:
            raise IndexError("lista vazia")
        return self._cauda

    def cons(self, x: Any) -> "Lista":
        return Lista(x, self)

    def __len__(self) -> int:
        return self._tam

    def __iter__(self) -> Iterator[Any]:
        no = self
        while not no.vazia:
            yield no._cabeca
            no = no._cauda

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, Lista):
            return NotImplemented
        if len(self) != len(outro):
            return False
        a, b = self, outro
        while not a.vazia:
            if a is b:
                return True  # sufixo compartilhado
            if a._cabeca != b._cabeca:
                return False
            a, b = a._cauda, b._cauda
        return True

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __repr__(self) -> str:
        return "Lista(" + ", ".join(map(repr, self)) + ")"

    def __getitem__(self, i: int) -> Any:
        if not 0 <= i < len(self):
            raise IndexError(i)
        no = self
        for _ in range(i):
            no = no._cauda
        return no._cabeca

    def __add__(self, outra: "Lista") -> "Lista":
        return anexar(self, outra)

    def mapear(self, f: Callable[[Any], Any]) -> "Lista":
        return de_iteravel(f(x) for x in self)

    def filtrar(self, pred: Callable[[Any], bool]) -> "Lista":
        return de_iteravel(x for x in self if pred(x))

    def dobrar_e(self, f: Callable[[Any, Any], Any], inicial: Any) -> Any:
        acc = inicial
        for x in self:
            acc = f(acc, x)
        return acc

    def dobrar_d(self, f: Callable[[Any, Any], Any], inicial: Any) -> Any:
        acc = inicial
        for x in self.reverter():
            acc = f(x, acc)
        return acc

    def reverter(self) -> "Lista":
        r = VAZIA
        for x in self:
            r = Lista(x, r)
        return r

    def pegar(self, n: int) -> "Lista":
        itens = []
        for x in self:
            if len(itens) >= n:
                break
            itens.append(x)
        return de_iteravel(itens)

    def largar(self, n: int) -> "Lista":
        no = self
        while n > 0 and not no.vazia:
            no = no._cauda
            n -= 1
        return no

    def atualizar(self, i: int, valor: Any) -> "Lista":
        """Nova lista com a posição i trocada; o sufixo após i é compartilhado."""
        if not 0 <= i < len(self):
            raise IndexError(i)
        prefixo = []
        no = self
        for _ in range(i):
            prefixo.append(no._cabeca)
            no = no._cauda
        r = Lista(valor, no._cauda)
        for x in reversed(prefixo):
            r = Lista(x, r)
        return r


VAZIA = Lista()


def de_iteravel(itens: Iterable[Any]) -> Lista:
    r = VAZIA
    for x in reversed(list(itens)):
        r = Lista(x, r)
    return r


def lista(*itens: Any) -> Lista:
    return de_iteravel(itens)


def anexar(a: Lista, b: Lista) -> Lista:
    """a ++ b: copia só a; b é compartilhada."""
    r = b
    for x in reversed(list(a)):
        r = Lista(x, r)
    return r
