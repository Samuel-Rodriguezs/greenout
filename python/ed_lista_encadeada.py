"""Lista encadeada simples."""
from __future__ import annotations

from typing import Any, Iterator, Optional


class No:
    def __init__(self, valor: Any, proximo: Optional["No"] = None) -> None:
        self.valor = valor
        self.proximo = proximo


class ListaEncadeada:
    def __init__(self) -> None:
        self._cabeca: Optional[No] = None
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def __iter__(self) -> Iterator[Any]:
        atual = self._cabeca
        while atual:
            yield atual.valor
            atual = atual.proximo

    def inserir_inicio(self, valor: Any) -> None:
        self._cabeca = No(valor, self._cabeca)
        self._tamanho += 1

    def inserir_fim(self, valor: Any) -> None:
        novo = No(valor)
        if self._cabeca is None:
            self._cabeca = novo
        else:
            atual = self._cabeca
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo
        self._tamanho += 1

    def buscar(self, valor: Any) -> int:
        """Retorna o índice da primeira ocorrência ou -1."""
        for i, v in enumerate(self):
            if v == valor:
                return i
        return -1

    def remover(self, valor: Any) -> None:
        """Remove a primeira ocorrência; ValueError se ausente."""
        anterior: Optional[No] = None
        atual = self._cabeca
        while atual:
            if atual.valor == valor:
                if anterior is None:
                    self._cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                self._tamanho -= 1
                return
            anterior, atual = atual, atual.proximo
        raise ValueError(f"valor não encontrado: {valor!r}")

    def inverter(self) -> None:
        anterior: Optional[No] = None
        atual = self._cabeca
        while atual:
            atual.proximo, anterior, atual = anterior, atual, atual.proximo
        self._cabeca = anterior
