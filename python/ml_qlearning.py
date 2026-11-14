"""Q-learning tabular em uma grade pequena (ambiente determinístico, seed no treino)."""
from __future__ import annotations

import random

ACOES = {"cima": (-1, 0), "baixo": (1, 0), "esquerda": (0, -1), "direita": (0, 1)}
NOMES = list(ACOES)


class Grade:
    """Grade com paredes, armadilhas (-10), objetivo (+10) e custo de passo (-1)."""

    def __init__(self, linhas: list[str]) -> None:
        """Símbolos: S início, G objetivo, # parede, X armadilha, . livre."""
        self.mapa = linhas
        self.altura, self.largura = len(linhas), len(linhas[0])
        self.inicio = self._achar("S")
        self.objetivo = self._achar("G")

    def _achar(self, c: str) -> tuple[int, int]:
        for i, l in enumerate(self.mapa):
            if c in l:
                return i, l.index(c)
        raise ValueError(f"símbolo {c!r} ausente no mapa")

    def passo(self, estado: tuple[int, int], acao: str) -> tuple[tuple[int, int], float, bool]:
        di, dj = ACOES[acao]
        i, j = estado[0] + di, estado[1] + dj
        if not (0 <= i < self.altura and 0 <= j < self.largura) or self.mapa[i][j] == "#":
            return estado, -1.0, False
        c = self.mapa[i][j]
        if c == "G":
            return (i, j), 10.0, True
        if c == "X":
            return (i, j), -10.0, True
        return (i, j), -1.0, False


def treinar(grade: Grade, episodios: int = 300, alfa: float = 0.5, gama: float = 0.95,
            epsilon: float = 0.2, seed: int = 0, max_passos: int = 100) -> dict:
    rng = random.Random(seed)
    Q: dict = {}
    for _ in range(episodios):
        s = grade.inicio
        for _ in range(max_passos):
            q = Q.setdefault(s, {a: 0.0 for a in NOMES})
            if rng.random() < epsilon:
                a = rng.choice(NOMES)
            else:
                melhor = max(q.values())
                a = rng.choice([x for x in NOMES if q[x] == melhor])
            s2, r, fim = grade.passo(s, a)
            q2 = Q.setdefault(s2, {x: 0.0 for x in NOMES})
            alvo = r if fim else r + gama * max(q2.values())
            q[a] += alfa * (alvo - q[a])
            s = s2
            if fim:
                break
    return Q


def politica_gulosa(Q: dict, estado: tuple[int, int]) -> str:
    q = Q.get(estado)
    if not q:
        return NOMES[0]
    return max(NOMES, key=lambda a: (q[a], -NOMES.index(a)))


def seguir_politica(grade: Grade, Q: dict, max_passos: int = 50) -> tuple[list[tuple[int, int]], float]:
    s = grade.inicio
    caminho, total = [s], 0.0
    for _ in range(max_passos):
        s, r, fim = grade.passo(s, politica_gulosa(Q, s))
        caminho.append(s)
        total += r
        if fim:
            break
    return caminho, total
