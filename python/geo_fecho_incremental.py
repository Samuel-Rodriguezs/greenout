"""Fecho convexo incremental: insere pontos um a um mantendo o fecho atual."""
from __future__ import annotations

from geo_convex_hull import andrew
from geo_orientacao import orientacao

Ponto = tuple[float, float]


class FechoIncremental:
    """Mantém os vértices do fecho em ordem anti-horária (sem colineares)."""

    def __init__(self, pontos: list[Ponto] | None = None) -> None:
        self._h: list[Ponto] = []
        for p in pontos or []:
            self.adicionar(p)

    @property
    def vertices(self) -> list[Ponto]:
        return list(self._h)

    def __len__(self) -> int:
        return len(self._h)

    def contem(self, p: Ponto) -> bool:
        """True se p está dentro do fecho ou sobre a borda."""
        h = self._h
        if not h:
            return False
        if len(h) < 3:
            return p in h or (
                len(h) == 2
                and orientacao(h[0], h[1], p) == 0
                and min(h[0], h[1]) <= p <= max(h[0], h[1])
            )
        n = len(h)
        return all(orientacao(h[i], h[(i + 1) % n], p) >= 0 for i in range(n))

    def adicionar(self, p: Ponto) -> bool:
        """Insere p; devolve True se o fecho mudou."""
        h = self._h
        if len(h) < 3:
            novo = andrew(h + [p])
            mudou = novo != h
            self._h = novo
            return mudou
        if self.contem(p):
            return False
        n = len(h)
        visivel = [orientacao(h[i], h[(i + 1) % n], p) <= 0 for i in range(n)]
        # início da sequência contígua de arestas visíveis
        inicio = next(i for i in range(n) if visivel[i] and not visivel[i - 1])
        k = 0
        while visivel[(inicio + k) % n]:
            k += 1
        # a sequência cobre as arestas inicio..inicio+k-1; os vértices internos saem
        mantidos = [h[(inicio + k + j) % n] for j in range(n - k + 1)]
        # mantidos vai de h[inicio+k] até h[inicio] (inclusive ambos)
        self._h = mantidos + [p]
        return True
