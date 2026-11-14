"""Lista duplamente encadeada."""
from __future__ import annotations

from typing import Any, Iterator, Optional


class No:
    def __init__(self, valor: Any) -> None:
        self.valor = valor
        self.anterior: Optional["No"] = None
        self.proximo: Optional["No"] = None


class ListaDupla:
    def __init__(self) -> None:
        self._cabeca: Optional[No] = None
        self._cauda: Optional[No] = None
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def __iter__(self) -> Iterator[Any]:
        atual = self._cabeca
        while atual:
            yield atual.valor
            atual = atual.proximo

    def reversa(self) -> Iterator[Any]:
        atual = self._cauda
        while atual:
            yield atual.valor
            atual = atual.anterior

    def adicionar_fim(self, valor: Any) -> None:
        no = No(valor)
        if self._cauda is None:
            self._cabeca = self._cauda = no
        else:
            no.anterior = self._cauda
            self._cauda.proximo = no
            self._cauda = no
        self._tamanho += 1

    def adicionar_inicio(self, valor: Any) -> None:
        no = No(valor)
        if self._cabeca is None:
            self._cabeca = self._cauda = no
        else:
            no.proximo = self._cabeca
            self._cabeca.anterior = no
            self._cabeca = no
        self._tamanho += 1

    def _desligar(self, no: No) -> Any:
        if no.anterior:
            no.anterior.proximo = no.proximo
        else:
            self._cabeca = no.proximo
        if no.proximo:
            no.proximo.anterior = no.anterior
        else:
            self._cauda = no.anterior
        self._tamanho -= 1
        return no.valor

    def remover_inicio(self) -> Any:
        if self._cabeca is None:
            raise IndexError("lista vazia")
        return self._desligar(self._cabeca)

    def remover_fim(self) -> Any:
        if self._cauda is None:
            raise IndexError("lista vazia")
        return self._desligar(self._cauda)

    def remover(self, valor: Any) -> None:
        atual = self._cabeca
        while atual:
            if atual.valor == valor:
                self._desligar(atual)
                return
            atual = atual.proximo
        raise ValueError(f"valor não encontrado: {valor!r}")
