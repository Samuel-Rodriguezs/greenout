"""Tetris: colisão, rotação, travamento e limpeza de linhas."""
from __future__ import annotations

import random

Celula = tuple[int, int]

FORMAS: dict[str, frozenset[Celula]] = {
    "I": frozenset({(0, 0), (0, 1), (0, 2), (0, 3)}),
    "O": frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}),
    "T": frozenset({(0, 1), (1, 0), (1, 1), (1, 2)}),
    "S": frozenset({(0, 1), (0, 2), (1, 0), (1, 1)}),
    "Z": frozenset({(0, 0), (0, 1), (1, 1), (1, 2)}),
    "J": frozenset({(0, 0), (1, 0), (1, 1), (1, 2)}),
    "L": frozenset({(0, 2), (1, 0), (1, 1), (1, 2)}),
}


def rotacionar(celulas: frozenset[Celula]) -> frozenset[Celula]:
    """Rotação de 90 graus no sentido horário, normalizada para começar em (0,0)."""
    giradas = {(c, -l) for l, c in celulas}
    minl = min(l for l, _ in giradas)
    minc = min(c for _, c in giradas)
    return frozenset((l - minl, c - minc) for l, c in giradas)


class Tetris:
    def __init__(self, linhas: int = 20, colunas: int = 10, rng: random.Random | None = None) -> None:
        self.linhas, self.colunas = linhas, colunas
        self.rng = rng or random.Random()
        self.tabuleiro: list[list[str]] = [[""] * colunas for _ in range(linhas)]
        self.pontos = 0
        self.linhas_limpas = 0
        self.fim = False
        self.nome = ""
        self.forma: frozenset[Celula] = frozenset()
        self.pos = (0, 0)
        self._nova_peca()

    def _nova_peca(self, nome: str | None = None) -> None:
        self.nome = nome or self.rng.choice(sorted(FORMAS))
        self.forma = FORMAS[self.nome]
        largura = max(c for _, c in self.forma) + 1
        self.pos = (0, (self.colunas - largura) // 2)
        if not self._cabe(self.forma, self.pos):
            self.fim = True

    def _cabe(self, forma: frozenset[Celula], pos: Celula) -> bool:
        for l, c in forma:
            r, k = l + pos[0], c + pos[1]
            if not (0 <= r < self.linhas and 0 <= k < self.colunas) or self.tabuleiro[r][k]:
                return False
        return True

    def celulas_peca(self) -> set[Celula]:
        return {(l + self.pos[0], c + self.pos[1]) for l, c in self.forma}

    def mover(self, dl: int, dc: int) -> bool:
        if self.fim:
            return False
        nova = (self.pos[0] + dl, self.pos[1] + dc)
        if self._cabe(self.forma, nova):
            self.pos = nova
            return True
        return False

    def rotacionar(self) -> bool:
        if self.fim:
            return False
        nova = rotacionar(self.forma)
        for desloc in (0, -1, 1, -2, 2, -3, 3):  # pequenos "wall kicks" horizontais
            p = (self.pos[0], self.pos[1] + desloc)
            if self._cabe(nova, p):
                self.forma, self.pos = nova, p
                return True
        return False

    def _travar(self) -> int:
        for l, c in self.celulas_peca():
            self.tabuleiro[l][c] = self.nome
        cheias = [i for i, lin in enumerate(self.tabuleiro) if all(lin)]
        for i in cheias:
            del self.tabuleiro[i]
            self.tabuleiro.insert(0, [""] * self.colunas)
        n = len(cheias)
        self.linhas_limpas += n
        self.pontos += (0, 100, 300, 500, 800)[n]
        self._nova_peca()
        return n

    def descer(self) -> int:
        """Desce uma linha; ao travar, retorna o número de linhas limpas (senão 0)."""
        if self.fim:
            return 0
        if self.mover(1, 0):
            return 0
        return self._travar()

    def queda_livre(self) -> int:
        while self.mover(1, 0):
            pass
        return self._travar()
