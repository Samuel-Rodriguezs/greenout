"""Árvore binária de busca (sem duplicados)."""
from __future__ import annotations

from typing import List, Optional


class No:
    def __init__(self, valor: int) -> None:
        self.valor = valor
        self.esq: Optional["No"] = None
        self.dir: Optional["No"] = None


class ArvoreBusca:
    def __init__(self) -> None:
        self._raiz: Optional[No] = None
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def inserir(self, valor: int) -> bool:
        """Insere o valor; retorna False se já existia."""
        if self._raiz is None:
            self._raiz = No(valor)
            self._tamanho += 1
            return True
        atual = self._raiz
        while True:
            if valor == atual.valor:
                return False
            if valor < atual.valor:
                if atual.esq is None:
                    atual.esq = No(valor)
                    break
                atual = atual.esq
            else:
                if atual.dir is None:
                    atual.dir = No(valor)
                    break
                atual = atual.dir
        self._tamanho += 1
        return True

    def buscar(self, valor: int) -> bool:
        atual = self._raiz
        while atual:
            if valor == atual.valor:
                return True
            atual = atual.esq if valor < atual.valor else atual.dir
        return False

    def em_ordem(self) -> List[int]:
        saida: List[int] = []

        def visitar(no: Optional[No]) -> None:
            if no:
                visitar(no.esq)
                saida.append(no.valor)
                visitar(no.dir)

        visitar(self._raiz)
        return saida

    def pre_ordem(self) -> List[int]:
        saida: List[int] = []

        def visitar(no: Optional[No]) -> None:
            if no:
                saida.append(no.valor)
                visitar(no.esq)
                visitar(no.dir)

        visitar(self._raiz)
        return saida

    def pos_ordem(self) -> List[int]:
        saida: List[int] = []

        def visitar(no: Optional[No]) -> None:
            if no:
                visitar(no.esq)
                visitar(no.dir)
                saida.append(no.valor)

        visitar(self._raiz)
        return saida

    def altura(self) -> int:
        def h(no: Optional[No]) -> int:
            return 0 if no is None else 1 + max(h(no.esq), h(no.dir))

        return h(self._raiz)

    def remover(self, valor: int) -> None:
        """Remove o valor; KeyError se ausente."""
        if not self.buscar(valor):
            raise KeyError(valor)
        self._raiz = self._remover(self._raiz, valor)
        self._tamanho -= 1

    def _remover(self, no: Optional[No], valor: int) -> Optional[No]:
        assert no is not None
        if valor < no.valor:
            no.esq = self._remover(no.esq, valor)
        elif valor > no.valor:
            no.dir = self._remover(no.dir, valor)
        else:
            if no.esq is None:
                return no.dir
            if no.dir is None:
                return no.esq
            sucessor = no.dir
            while sucessor.esq:
                sucessor = sucessor.esq
            no.valor = sucessor.valor
            no.dir = self._remover(no.dir, sucessor.valor)
        return no
