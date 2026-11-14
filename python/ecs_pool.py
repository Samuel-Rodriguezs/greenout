"""Pool de objetos reutilizáveis com capacidade máxima."""
from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class PoolObjetos(Generic[T]):
    def __init__(
        self,
        fabrica: Callable[[], T],
        resetar: Callable[[T], None] | None = None,
        capacidade: int | None = None,
    ) -> None:
        if capacidade is not None and capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self._fabrica = fabrica
        self._resetar = resetar
        self._capacidade = capacidade
        self._livres: list[T] = []
        self._em_uso: dict[int, T] = {}
        self.criados = 0

    def adquirir(self) -> T:
        if self._livres:
            obj = self._livres.pop()
        else:
            if self._capacidade is not None and self.criados >= self._capacidade:
                raise RuntimeError("pool esgotado")
            obj = self._fabrica()
            self.criados += 1
        self._em_uso[id(obj)] = obj
        return obj

    def liberar(self, obj: T) -> None:
        if id(obj) not in self._em_uso:
            raise ValueError("objeto não pertence ao pool ou já foi liberado")
        del self._em_uso[id(obj)]
        if self._resetar is not None:
            self._resetar(obj)
        self._livres.append(obj)

    @property
    def em_uso(self) -> int:
        return len(self._em_uso)

    @property
    def livres(self) -> int:
        return len(self._livres)
