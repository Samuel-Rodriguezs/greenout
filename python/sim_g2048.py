"""Lógica do jogo 2048."""
from __future__ import annotations

import random

Grade = list[list[int]]


def deslizar_linha(linha: list[int]) -> tuple[list[int], int]:
    """Desliza para a esquerda; retorna (nova linha, pontos)."""
    vals = [v for v in linha if v]
    saida: list[int] = []
    pontos = 0
    i = 0
    while i < len(vals):
        if i + 1 < len(vals) and vals[i] == vals[i + 1]:
            saida.append(vals[i] * 2)
            pontos += vals[i] * 2
            i += 2
        else:
            saida.append(vals[i])
            i += 1
    return saida + [0] * (len(linha) - len(saida)), pontos


class Jogo2048:
    def __init__(self, n: int = 4, rng: random.Random | None = None) -> None:
        self.n = n
        self.rng = rng or random.Random()
        self.grade: Grade = [[0] * n for _ in range(n)]
        self.pontos = 0
        self._nova_peca()
        self._nova_peca()

    def _nova_peca(self) -> None:
        vazias = [(l, c) for l in range(self.n) for c in range(self.n) if not self.grade[l][c]]
        if not vazias:
            return
        l, c = self.rng.choice(vazias)
        self.grade[l][c] = 4 if self.rng.random() < 0.1 else 2

    def _aplicar(self, direcao: str) -> tuple[Grade, int]:
        g = self.grade
        if direcao == "esquerda":
            linhas = [r[:] for r in g]
        elif direcao == "direita":
            linhas = [r[::-1] for r in g]
        elif direcao == "cima":
            linhas = [list(col) for col in zip(*g)]
        elif direcao == "baixo":
            linhas = [list(col)[::-1] for col in zip(*g)]
        else:
            raise ValueError("direção inválida")
        total = 0
        novas = []
        for l in linhas:
            nl, p = deslizar_linha(l)
            novas.append(nl)
            total += p
        if direcao == "direita":
            res = [r[::-1] for r in novas]
        elif direcao == "cima":
            res = [list(r) for r in zip(*novas)]
        elif direcao == "baixo":
            res = [list(r) for r in zip(*[x[::-1] for x in novas])]
        else:
            res = novas
        return res, total

    def mover(self, direcao: str) -> bool:
        nova, p = self._aplicar(direcao)
        if nova == self.grade:
            return False
        self.grade = nova
        self.pontos += p
        self._nova_peca()
        return True

    @property
    def venceu(self) -> bool:
        return any(v >= 2048 for r in self.grade for v in r)

    @property
    def fim(self) -> bool:
        return all(self._aplicar(d)[0] == self.grade for d in ("esquerda", "direita", "cima", "baixo"))
