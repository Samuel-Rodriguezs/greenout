"""Cobertura exata (Algoritmo X de Knuth com dancing links) aplicada a pentominós."""
from __future__ import annotations

from typing import Iterator, Optional

Celula = tuple[int, int]


class DLX:
    """Matriz de listas duplamente encadeadas (colunas primárias numeradas de 1)."""

    def __init__(self, n_colunas: int) -> None:
        n = n_colunas
        self.L = [i - 1 for i in range(n + 1)]
        self.R = [i + 1 for i in range(n + 1)]
        self.L[0] = n
        self.R[n] = 0
        self.U = list(range(n + 1))
        self.D = list(range(n + 1))
        self.C = list(range(n + 1))
        self.S = [0] * (n + 1)
        self.linha: list[int] = [-1] * (n + 1)

    def adicionar_linha(self, id_linha: int, colunas: list[int]) -> None:
        primeiro = -1
        for c in colunas:
            no = len(self.C)
            self.C.append(c)
            self.U.append(self.U[c])
            self.D.append(c)
            self.D[self.U[c]] = no
            self.U[c] = no
            self.S[c] += 1
            self.linha.append(id_linha)
            self.L.append(no)
            self.R.append(no)
            if primeiro < 0:
                primeiro = no
            else:
                ultimo = self.L[primeiro]
                self.L[no], self.R[no] = ultimo, primeiro
                self.R[ultimo] = no
                self.L[primeiro] = no

    def _cobrir(self, c: int) -> None:
        self.R[self.L[c]], self.L[self.R[c]] = self.R[c], self.L[c]
        i = self.D[c]
        while i != c:
            j = self.R[i]
            while j != i:
                self.D[self.U[j]], self.U[self.D[j]] = self.D[j], self.U[j]
                self.S[self.C[j]] -= 1
                j = self.R[j]
            i = self.D[i]

    def _descobrir(self, c: int) -> None:
        i = self.U[c]
        while i != c:
            j = self.L[i]
            while j != i:
                self.S[self.C[j]] += 1
                self.D[self.U[j]] = self.U[self.D[j]] = j
                j = self.L[j]
            i = self.U[i]
        self.R[self.L[c]] = self.L[self.R[c]] = c

    def solucoes(self) -> Iterator[list[int]]:
        parcial: list[int] = []

        def buscar() -> Iterator[list[int]]:
            if self.R[0] == 0:
                yield [self.linha[n] for n in parcial]
                return
            c = j = self.R[0]
            while j != 0:  # heurística: coluna com menos opções
                if self.S[j] < self.S[c]:
                    c = j
                j = self.R[j]
            if self.S[c] == 0:
                return
            self._cobrir(c)
            r = self.D[c]
            while r != c:
                parcial.append(r)
                j = self.R[r]
                while j != r:
                    self._cobrir(self.C[j])
                    j = self.R[j]
                yield from buscar()
                j = self.L[r]
                while j != r:
                    self._descobrir(self.C[j])
                    j = self.L[j]
                parcial.pop()
                r = self.D[r]
            self._descobrir(c)

        yield from buscar()


def cobertura_exata(universo: list, subconjuntos: list[set]) -> Iterator[list[int]]:
    """Gera listas de índices de subconjuntos que particionam exatamente o universo."""
    idx = {x: i + 1 for i, x in enumerate(universo)}
    dlx = DLX(len(universo))
    for k, s in enumerate(subconjuntos):
        if s and all(x in idx for x in s):
            dlx.adicionar_linha(k, sorted(idx[x] for x in s))
    yield from dlx.solucoes()


# --- Pentominós -----------------------------------------------------------

PENTOMINOS: dict[str, list[Celula]] = {
    "F": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    "I": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    "L": [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    "N": [(0, 1), (1, 1), (2, 0), (2, 1), (3, 0)],
    "P": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    "T": [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    "U": [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
    "V": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    "W": [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    "X": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    "Y": [(0, 1), (1, 0), (1, 1), (2, 1), (3, 1)],
    "Z": [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
}


def _normalizar(celulas: list[Celula]) -> tuple[Celula, ...]:
    mr = min(r for r, _ in celulas)
    mc = min(c for _, c in celulas)
    return tuple(sorted((r - mr, c - mc) for r, c in celulas))


def orientacoes(forma: list[Celula]) -> list[tuple[Celula, ...]]:
    """As até 8 orientações distintas (rotações e reflexões)."""
    vistas = set()
    atual = list(forma)
    for _ in range(2):
        for _ in range(4):
            atual = [(c, -r) for r, c in atual]
            vistas.add(_normalizar(atual))
        atual = [(r, -c) for r, c in atual]
    return sorted(vistas)


def posicionamentos(forma: list[Celula], regiao: set[Celula]) -> list[frozenset[Celula]]:
    saida = set()
    for ori in orientacoes(forma):
        for r0, c0 in regiao:
            colocada = frozenset((r0 + r, c0 + c) for r, c in ori)
            if colocada <= regiao:
                saida.add(colocada)
    return sorted(saida, key=sorted)


def retangulo(linhas: int, colunas: int) -> set[Celula]:
    return {(r, c) for r in range(linhas) for c in range(colunas)}


def _montar(regiao: set[Celula], pecas: list[str]):
    universo: list = [("p", nome) for nome in pecas] + sorted(regiao)
    opcoes = [(nome, pos) for nome in pecas for pos in posicionamentos(PENTOMINOS[nome], regiao)]
    subconjuntos = [{("p", nome)} | set(pos) for nome, pos in opcoes]
    return universo, opcoes, subconjuntos


def ladrilhos(regiao: set[Celula], pecas: list[str]) -> Iterator[dict[Celula, str]]:
    """Gera os ladrilhamentos da região usando cada peça de `pecas` exatamente uma vez."""
    if len(regiao) != 5 * len(pecas) or len(set(pecas)) != len(pecas):
        return
    universo, opcoes, subconjuntos = _montar(regiao, pecas)
    for sol in cobertura_exata(universo, subconjuntos):
        tabuleiro: dict[Celula, str] = {}
        for k in sol:
            nome, pos = opcoes[k]
            for cel in pos:
                tabuleiro[cel] = nome
        yield tabuleiro


def ladrilhar(regiao: set[Celula], pecas: list[str]) -> Optional[dict[Celula, str]]:
    return next(ladrilhos(regiao, pecas), None)


def contar_ladrilhamentos(regiao: set[Celula], pecas: list[str]) -> int:
    return sum(1 for _ in ladrilhos(regiao, pecas))
