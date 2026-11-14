"""Jogo da cobrinha (snake) em grade."""
from __future__ import annotations

import random
from collections import deque

Pos = tuple[int, int]
DIRS: dict[str, Pos] = {"cima": (-1, 0), "baixo": (1, 0), "esquerda": (0, -1), "direita": (0, 1)}


class Snake:
    def __init__(self, linhas: int = 10, colunas: int = 10, rng: random.Random | None = None) -> None:
        self.linhas, self.colunas = linhas, colunas
        self.rng = rng or random.Random()
        self.corpo: deque[Pos] = deque([(linhas // 2, colunas // 2 - i) for i in range(3)])
        self.direcao = "direita"
        self.pontos = 0
        self.vivo = True
        self.comida: Pos | None = None
        self._sortear_comida()

    def _sortear_comida(self) -> None:
        livres = [(l, c) for l in range(self.linhas) for c in range(self.colunas) if (l, c) not in self.corpo]
        self.comida = self.rng.choice(livres) if livres else None

    def virar(self, direcao: str) -> None:
        if direcao not in DIRS:
            raise ValueError("direção inválida")
        atual, nova = DIRS[self.direcao], DIRS[direcao]
        if (atual[0] + nova[0], atual[1] + nova[1]) != (0, 0):
            self.direcao = direcao

    def passo(self) -> bool:
        if not self.vivo:
            return False
        dl, dc = DIRS[self.direcao]
        l, c = self.corpo[0]
        nova = (l + dl, c + dc)
        crescer = nova == self.comida
        cauda = None if crescer else self.corpo[-1]
        if not (0 <= nova[0] < self.linhas and 0 <= nova[1] < self.colunas) or \
                (nova in self.corpo and nova != cauda):
            self.vivo = False
            return False
        self.corpo.appendleft(nova)
        if crescer:
            self.pontos += 1
            self._sortear_comida()
        else:
            self.corpo.pop()
        return True
