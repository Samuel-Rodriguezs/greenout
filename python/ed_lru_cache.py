"""Cache LRU (menos recentemente usado) com capacidade fixa."""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Hashable, List, Optional


class LRUCache:
    def __init__(self, capacidade: int) -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self._capacidade = capacidade
        self._dados: "OrderedDict[Hashable, Any]" = OrderedDict()

    def __len__(self) -> int:
        return len(self._dados)

    def __contains__(self, chave: Hashable) -> bool:
        return chave in self._dados

    def obter(self, chave: Hashable, padrao: Optional[Any] = None) -> Any:
        """Retorna o valor (marcando-o como recente) ou `padrao`."""
        if chave not in self._dados:
            return padrao
        self._dados.move_to_end(chave)
        return self._dados[chave]

    def colocar(self, chave: Hashable, valor: Any) -> None:
        if chave in self._dados:
            self._dados.move_to_end(chave)
        self._dados[chave] = valor
        if len(self._dados) > self._capacidade:
            self._dados.popitem(last=False)

    def chaves(self) -> List[Hashable]:
        """Chaves da menos para a mais recentemente usada."""
        return list(self._dados)
