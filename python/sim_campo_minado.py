"""Campo minado: minas posicionadas no primeiro clique, flood fill."""
from __future__ import annotations

import random

Pos = tuple[int, int]


class CampoMinado:
    def __init__(self, linhas: int = 9, colunas: int = 9, minas: int = 10,
                 rng: random.Random | None = None) -> None:
        if minas >= linhas * colunas:
            raise ValueError("minas demais")
        self.linhas, self.colunas, self.n_minas = linhas, colunas, minas
        self.rng = rng or random.Random()
        self.minas: set[Pos] = set()
        self.reveladas: set[Pos] = set()
        self.bandeiras: set[Pos] = set()
        self.perdeu = False
        self._iniciado = False

    def vizinhos(self, pos: Pos) -> list[Pos]:
        l, c = pos
        return [(l + a, c + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                if (a or b) and 0 <= l + a < self.linhas and 0 <= c + b < self.colunas]

    def contagem(self, pos: Pos) -> int:
        return sum(v in self.minas for v in self.vizinhos(pos))

    def _plantar(self, seguro: Pos) -> None:
        candidatas = [(l, c) for l in range(self.linhas) for c in range(self.colunas) if (l, c) != seguro]
        self.minas = set(self.rng.sample(candidatas, self.n_minas))
        self._iniciado = True

    def alternar_bandeira(self, pos: Pos) -> None:
        if pos in self.reveladas:
            return
        self.bandeiras ^= {pos}

    def revelar(self, pos: Pos) -> None:
        if self.perdeu or self.venceu or pos in self.bandeiras or pos in self.reveladas:
            return
        if not (0 <= pos[0] < self.linhas and 0 <= pos[1] < self.colunas):
            raise ValueError("fora do campo")
        if not self._iniciado:
            self._plantar(pos)
        if pos in self.minas:
            self.perdeu = True
            self.reveladas.add(pos)
            return
        pilha = [pos]
        while pilha:
            p = pilha.pop()
            if p in self.reveladas or p in self.bandeiras:
                continue
            self.reveladas.add(p)
            if self.contagem(p) == 0:
                pilha.extend(v for v in self.vizinhos(p) if v not in self.reveladas)

    @property
    def venceu(self) -> bool:
        return self._iniciado and not self.perdeu and \
            len(self.reveladas) == self.linhas * self.colunas - self.n_minas

    def render(self) -> list[str]:
        saida = []
        for l in range(self.linhas):
            linha = ""
            for c in range(self.colunas):
                p = (l, c)
                if p in self.reveladas:
                    linha += "*" if p in self.minas else (str(self.contagem(p)) if self.contagem(p) else " ")
                elif p in self.bandeiras:
                    linha += "F"
                else:
                    linha += "#"
            saida.append(linha)
        return saida
