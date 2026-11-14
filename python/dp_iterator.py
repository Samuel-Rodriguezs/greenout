"""Iterator: paginação sobre uma coleção de pedidos e iterador de árvore em ordem."""
from __future__ import annotations

from typing import Iterator, Optional, Sequence, TypeVar

T = TypeVar("T")


class Paginas(Sequence[T]):
    """Coleção iterável por páginas de tamanho fixo."""

    def __init__(self, itens: Sequence[T], tamanho: int) -> None:
        if tamanho <= 0:
            raise ValueError("tamanho de página inválido")
        self._itens = itens
        self._tamanho = tamanho

    def __len__(self) -> int:
        return -(-len(self._itens) // self._tamanho)

    def __getitem__(self, i):  # type: ignore[override]
        if isinstance(i, slice):
            return [self[j] for j in range(*i.indices(len(self)))]
        if i < 0:
            i += len(self)
        if not 0 <= i < len(self):
            raise IndexError(i)
        return list(self._itens[i * self._tamanho:(i + 1) * self._tamanho])


class NoBst:
    def __init__(self, valor: int) -> None:
        self.valor = valor
        self.esq: Optional["NoBst"] = None
        self.dir: Optional["NoBst"] = None


class ArvoreOrdenada:
    def __init__(self) -> None:
        self._raiz: Optional[NoBst] = None

    def inserir(self, valor: int) -> None:
        novo = NoBst(valor)
        if self._raiz is None:
            self._raiz = novo
            return
        atual = self._raiz
        while True:
            lado = "esq" if valor < atual.valor else "dir"
            prox = getattr(atual, lado)
            if prox is None:
                setattr(atual, lado, novo)
                return
            atual = prox

    def __iter__(self) -> Iterator[int]:
        pilha: list[NoBst] = []
        atual = self._raiz
        while pilha or atual:
            while atual:
                pilha.append(atual)
                atual = atual.esq
            atual = pilha.pop()
            yield atual.valor
            atual = atual.dir
