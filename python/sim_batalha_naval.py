"""Batalha naval: posicionamento aleatório e tiros."""
from __future__ import annotations

import random

Pos = tuple[int, int]


class BatalhaNaval:
    def __init__(self, tamanho: int = 10, navios: tuple[int, ...] = (5, 4, 3, 3, 2),
                 rng: random.Random | None = None) -> None:
        self.tamanho = tamanho
        self.rng = rng or random.Random()
        self.navios: list[set[Pos]] = []
        self.tiros: set[Pos] = set()
        for n in navios:
            self._posicionar(n)

    def _posicionar(self, n: int) -> None:
        ocupadas = {p for navio in self.navios for p in navio}
        for _ in range(10000):
            horiz = self.rng.random() < 0.5
            l = self.rng.randrange(self.tamanho - (0 if horiz else n - 1))
            c = self.rng.randrange(self.tamanho - (n - 1 if horiz else 0))
            cels = {(l, c + i) if horiz else (l + i, c) for i in range(n)}
            if not cels & ocupadas:
                self.navios.append(cels)
                return
        raise RuntimeError("não foi possível posicionar navio")

    def atirar(self, pos: Pos) -> str:
        """Retorna 'agua', 'acertou' ou 'afundou'."""
        l, c = pos
        if not (0 <= l < self.tamanho and 0 <= c < self.tamanho):
            raise ValueError("fora do tabuleiro")
        if pos in self.tiros:
            raise ValueError("posição já atingida")
        self.tiros.add(pos)
        for navio in self.navios:
            if pos in navio:
                return "afundou" if navio <= self.tiros else "acertou"
        return "agua"

    @property
    def venceu(self) -> bool:
        return all(n <= self.tiros for n in self.navios)
