"""Formiga de Langton em grade toroidal."""
from __future__ import annotations

# direções no sentido horário: norte, leste, sul, oeste
DIRECOES = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class FormigaLangton:
    def __init__(self, linhas: int = 20, colunas: int = 20, pos: tuple[int, int] | None = None,
                 direcao: int = 0) -> None:
        self.linhas, self.colunas = linhas, colunas
        self.pretas: set[tuple[int, int]] = set()
        self.pos = pos if pos is not None else (linhas // 2, colunas // 2)
        self.direcao = direcao % 4
        self.passos = 0

    def passo(self) -> None:
        if self.pos in self.pretas:
            self.direcao = (self.direcao - 1) % 4  # célula preta: vira à esquerda
            self.pretas.discard(self.pos)
        else:
            self.direcao = (self.direcao + 1) % 4  # célula branca: vira à direita
            self.pretas.add(self.pos)
        dl, dc = DIRECOES[self.direcao]
        self.pos = ((self.pos[0] + dl) % self.linhas, (self.pos[1] + dc) % self.colunas)
        self.passos += 1

    def executar(self, n: int) -> None:
        for _ in range(n):
            self.passo()

    def render(self) -> list[str]:
        saida = []
        for l in range(self.linhas):
            linha = ""
            for c in range(self.colunas):
                if (l, c) == self.pos:
                    linha += "@"
                else:
                    linha += "#" if (l, c) in self.pretas else "."
            saida.append(linha)
        return saida
