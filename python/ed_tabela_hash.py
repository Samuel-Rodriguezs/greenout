"""Tabela hash com encadeamento separado e redimensionamento."""
from __future__ import annotations

from typing import Any, Hashable, Iterator, List, Tuple


class TabelaHash:
    def __init__(self, capacidade: int = 8) -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self._baldes: List[List[Tuple[Hashable, Any]]] = [[] for _ in range(capacidade)]
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def __contains__(self, chave: Hashable) -> bool:
        return any(k == chave for k, _ in self._balde(chave))

    def _balde(self, chave: Hashable) -> List[Tuple[Hashable, Any]]:
        return self._baldes[hash(chave) % len(self._baldes)]

    def colocar(self, chave: Hashable, valor: Any) -> None:
        balde = self._balde(chave)
        for i, (k, _) in enumerate(balde):
            if k == chave:
                balde[i] = (chave, valor)
                return
        balde.append((chave, valor))
        self._tamanho += 1
        if self._tamanho > 0.75 * len(self._baldes):
            self._redimensionar()

    def obter(self, chave: Hashable) -> Any:
        for k, v in self._balde(chave):
            if k == chave:
                return v
        raise KeyError(chave)

    def remover(self, chave: Hashable) -> Any:
        balde = self._balde(chave)
        for i, (k, v) in enumerate(balde):
            if k == chave:
                del balde[i]
                self._tamanho -= 1
                return v
        raise KeyError(chave)

    def itens(self) -> Iterator[Tuple[Hashable, Any]]:
        for balde in self._baldes:
            yield from balde

    def _redimensionar(self) -> None:
        antigos = list(self.itens())
        self._baldes = [[] for _ in range(len(self._baldes) * 2)]
        for k, v in antigos:
            self._balde(k).append((k, v))
