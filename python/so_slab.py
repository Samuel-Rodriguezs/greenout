"""Alocador slab: cache de objetos de tamanho fixo organizado em slabs.

Cada slab ocupa `tamanho_slab` bytes e guarda `tamanho_slab // tamanho_objeto`
objetos. Alocação prefere slabs parciais, depois vazios, e só então cria um
novo. Liberar nunca devolve memória ao sistema até `encolher()` ser chamado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class SemMemoria(Exception):
    pass


@dataclass
class Slab:
    id: int
    capacidade: int
    livres: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.livres:
            self.livres = list(range(self.capacidade))

    @property
    def usados(self) -> int:
        return self.capacidade - len(self.livres)

    @property
    def estado(self) -> str:
        if self.usados == 0:
            return "vazio"
        return "cheio" if not self.livres else "parcial"


class CacheSlab:
    def __init__(
        self,
        tamanho_objeto: int,
        tamanho_slab: int = 4096,
        max_slabs: Optional[int] = None,
    ) -> None:
        if tamanho_objeto <= 0 or tamanho_objeto > tamanho_slab:
            raise ValueError("tamanho_objeto deve caber no slab")
        self.tamanho_objeto = tamanho_objeto
        self.tamanho_slab = tamanho_slab
        self.max_slabs = max_slabs
        self.por_slab = tamanho_slab // tamanho_objeto
        self.slabs: dict[int, Slab] = {}
        self._proximo_id = 0

    @property
    def desperdicio_por_slab(self) -> int:
        return self.tamanho_slab % self.tamanho_objeto

    def _novo_slab(self) -> Slab:
        if self.max_slabs is not None and len(self.slabs) >= self.max_slabs:
            raise SemMemoria("limite de slabs atingido")
        s = Slab(self._proximo_id, self.por_slab)
        self.slabs[s.id] = s
        self._proximo_id += 1
        return s

    def alocar(self) -> tuple[int, int]:
        """Devolve o handle (id_do_slab, posição)."""
        ordem = sorted(self.slabs.values(), key=lambda s: s.id)
        escolhido = next((s for s in ordem if s.estado == "parcial"), None)
        if escolhido is None:
            escolhido = next((s for s in ordem if s.estado == "vazio"), None)
        if escolhido is None:
            escolhido = self._novo_slab()
        return escolhido.id, escolhido.livres.pop(0)

    def liberar(self, handle: tuple[int, int]) -> None:
        sid, pos = handle
        slab = self.slabs.get(sid)
        if slab is None or not 0 <= pos < slab.capacidade or pos in slab.livres:
            raise KeyError(handle)  # inexistente ou liberação dupla
        slab.livres.append(pos)
        slab.livres.sort()

    def encolher(self) -> int:
        """Devolve os slabs vazios ao sistema; retorna quantos foram liberados."""
        vazios = [i for i, s in self.slabs.items() if s.estado == "vazio"]
        for i in vazios:
            del self.slabs[i]
        return len(vazios)

    def contagem(self) -> dict[str, int]:
        c = {"cheio": 0, "parcial": 0, "vazio": 0}
        for s in self.slabs.values():
            c[s.estado] += 1
        return c

    def objetos_em_uso(self) -> int:
        return sum(s.usados for s in self.slabs.values())

    def bytes_reservados(self) -> int:
        return len(self.slabs) * self.tamanho_slab
