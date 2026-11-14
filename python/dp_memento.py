"""Memento: snapshots do estado de um carrinho de compras."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SnapshotCarrinho:
    itens: tuple[tuple[str, int], ...]
    cupom: str | None


class Carrinho:
    def __init__(self) -> None:
        self._itens: dict[str, int] = {}
        self.cupom: str | None = None

    def adicionar(self, produto: str, qtd: int = 1) -> None:
        self._itens[produto] = self._itens.get(produto, 0) + qtd

    def remover(self, produto: str) -> None:
        self._itens.pop(produto, None)

    @property
    def itens(self) -> dict[str, int]:
        return dict(self._itens)

    def salvar(self) -> SnapshotCarrinho:
        return SnapshotCarrinho(tuple(sorted(self._itens.items())), self.cupom)

    def restaurar(self, snap: SnapshotCarrinho) -> None:
        self._itens = dict(snap.itens)
        self.cupom = snap.cupom


class Zelador:
    def __init__(self, carrinho: Carrinho) -> None:
        self._carrinho = carrinho
        self._pilha: list[SnapshotCarrinho] = []

    def checkpoint(self) -> None:
        self._pilha.append(self._carrinho.salvar())

    def voltar(self) -> bool:
        if not self._pilha:
            return False
        self._carrinho.restaurar(self._pilha.pop())
        return True
