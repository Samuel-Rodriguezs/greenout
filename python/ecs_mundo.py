"""Mundo ECS: entidades, componentes e consultas por assinatura de componentes."""
from __future__ import annotations

from typing import Any, Iterator, TypeVar

T = TypeVar("T")


class Mundo:
    """Armazena componentes indexados por tipo; entidades são inteiros."""

    def __init__(self) -> None:
        self._proximo: int = 1
        self._vivas: set[int] = set()
        self._armazens: dict[type, dict[int, Any]] = {}

    def criar(self, *componentes: Any) -> int:
        ent = self._proximo
        self._proximo += 1
        self._vivas.add(ent)
        for c in componentes:
            self.adicionar(ent, c)
        return ent

    def existe(self, ent: int) -> bool:
        return ent in self._vivas

    def destruir(self, ent: int) -> None:
        if ent not in self._vivas:
            raise KeyError(f"entidade inexistente: {ent}")
        self._vivas.discard(ent)
        for arm in self._armazens.values():
            arm.pop(ent, None)

    def adicionar(self, ent: int, comp: Any) -> None:
        if ent not in self._vivas:
            raise KeyError(f"entidade inexistente: {ent}")
        self._armazens.setdefault(type(comp), {})[ent] = comp

    def remover(self, ent: int, tipo: type) -> None:
        arm = self._armazens.get(tipo, {})
        if ent not in arm:
            raise KeyError(f"entidade {ent} sem componente {tipo.__name__}")
        del arm[ent]

    def obter(self, ent: int, tipo: type[T]) -> T:
        try:
            return self._armazens[tipo][ent]
        except KeyError:
            raise KeyError(f"entidade {ent} sem componente {tipo.__name__}") from None

    def tem(self, ent: int, *tipos: type) -> bool:
        return all(ent in self._armazens.get(t, {}) for t in tipos)

    def consultar(self, *tipos: type, excluir: tuple[type, ...] = ()) -> Iterator[tuple[int, tuple[Any, ...]]]:
        """Itera (entidade, componentes) em ordem crescente de id.

        Entidades devem ter todos os `tipos` e nenhum de `excluir`.
        """
        if not tipos:
            raise ValueError("informe ao menos um tipo de componente")
        arms = [self._armazens.get(t, {}) for t in tipos]
        menor = min(arms, key=len)
        candidatas = sorted(e for e in menor if all(e in a for a in arms))
        for e in candidatas:
            if any(e in self._armazens.get(x, {}) for x in excluir):
                continue
            yield e, tuple(a[e] for a in arms)

    def __len__(self) -> int:
        return len(self._vivas)
