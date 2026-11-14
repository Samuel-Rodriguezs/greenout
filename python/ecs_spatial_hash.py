"""Grade espacial (spatial hash) para consultas de vizinhança em 2D."""
from __future__ import annotations

from math import floor
from typing import Hashable, Iterator


class SpatialHash:
    """Indexa objetos por retângulo (x, y, w, h) em células de tamanho fixo."""

    def __init__(self, tamanho_celula: float) -> None:
        if tamanho_celula <= 0:
            raise ValueError("tamanho_celula deve ser positivo")
        self.t = tamanho_celula
        self._celulas: dict[tuple[int, int], set[Hashable]] = {}
        self._caixas: dict[Hashable, tuple[float, float, float, float]] = {}

    def _faixa(self, x: float, y: float, w: float, h: float) -> Iterator[tuple[int, int]]:
        # extremo direito exclusivo: um objeto que apenas toca a célula vizinha não a ocupa
        x0, y0 = floor(x / self.t), floor(y / self.t)
        x1 = max(x0, _teto(( x + w) / self.t) - 1)
        y1 = max(y0, _teto((y + h) / self.t) - 1)
        for i in range(x0, x1 + 1):
            for j in range(y0, y1 + 1):
                yield (i, j)

    def inserir(self, obj: Hashable, x: float, y: float, w: float = 0.0, h: float = 0.0) -> None:
        if obj in self._caixas:
            self.remover(obj)
        self._caixas[obj] = (x, y, w, h)
        for c in self._faixa(x, y, w, h):
            self._celulas.setdefault(c, set()).add(obj)

    def remover(self, obj: Hashable) -> None:
        x, y, w, h = self._caixas.pop(obj)
        for c in self._faixa(x, y, w, h):
            s = self._celulas.get(c)
            if s is not None:
                s.discard(obj)
                if not s:
                    del self._celulas[c]

    def mover(self, obj: Hashable, x: float, y: float) -> None:
        _, _, w, h = self._caixas[obj]
        self.inserir(obj, x, y, w, h)

    def consultar(self, x: float, y: float, w: float = 0.0, h: float = 0.0) -> set[Hashable]:
        """Objetos cujas caixas intersectam o retângulo (teste exato, não só por célula)."""
        achados: set[Hashable] = set()
        for c in self._faixa(x, y, w, h):
            for obj in self._celulas.get(c, ()):
                if obj in achados:
                    continue
                ox, oy, ow, oh = self._caixas[obj]
                if ox <= x + w and x <= ox + ow and oy <= y + h and y <= oy + oh:
                    achados.add(obj)
        return achados

    def pares_candidatos(self) -> set[tuple[Hashable, Hashable]]:
        """Pares de objetos que dividem ao menos uma célula (fase ampla)."""
        pares: set[tuple[Hashable, Hashable]] = set()
        for s in self._celulas.values():
            itens = sorted(s, key=repr)
            for i, a in enumerate(itens):
                for b in itens[i + 1:]:
                    pares.add((a, b))
        return pares

    def __len__(self) -> int:
        return len(self._caixas)


def _teto(v: float) -> int:
    return -floor(-v)
