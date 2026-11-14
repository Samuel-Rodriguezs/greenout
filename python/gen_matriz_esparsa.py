"""Matrizes esparsas aleatórias nos formatos COO e CSR, com multiplicação por vetor."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class CSR:
    linhas: int
    colunas: int
    valores: tuple[float, ...]
    indices_coluna: tuple[int, ...]
    ponteiros_linha: tuple[int, ...]  # len = linhas + 1

    @property
    def nnz(self) -> int:
        return len(self.valores)

    def multiplicar(self, x: list[float]) -> list[float]:
        if len(x) != self.colunas:
            raise ValueError("dimensão do vetor incompatível")
        y = []
        for i in range(self.linhas):
            ini, fim = self.ponteiros_linha[i], self.ponteiros_linha[i + 1]
            y.append(sum(self.valores[k] * x[self.indices_coluna[k]] for k in range(ini, fim)))
        return y

    def para_densa(self) -> list[list[float]]:
        m = [[0.0] * self.colunas for _ in range(self.linhas)]
        for i in range(self.linhas):
            for k in range(self.ponteiros_linha[i], self.ponteiros_linha[i + 1]):
                m[i][self.indices_coluna[k]] = self.valores[k]
        return m


def gerar_coo(
    rng: random.Random, linhas: int, colunas: int, densidade: float
) -> list[tuple[int, int, float]]:
    """Triplas (i, j, valor) ordenadas, sem posições repetidas, com round(densidade * total) entradas."""
    if linhas < 1 or colunas < 1:
        raise ValueError("dimensões devem ser positivas")
    if not 0.0 <= densidade <= 1.0:
        raise ValueError("densidade deve estar em [0, 1]")
    total = linhas * colunas
    k = round(densidade * total)
    posicoes = sorted(rng.sample(range(total), k))
    return [
        (p // colunas, p % colunas, round(rng.uniform(-10, 10), 3) or 1.0)
        for p in posicoes
    ]


def coo_para_csr(linhas: int, colunas: int, coo: list[tuple[int, int, float]]) -> CSR:
    ordenado = sorted(coo, key=lambda t: (t[0], t[1]))
    ponteiros = [0] * (linhas + 1)
    for i, j, _ in ordenado:
        if not (0 <= i < linhas and 0 <= j < colunas):
            raise ValueError("entrada fora das dimensões")
        ponteiros[i + 1] += 1
    for i in range(linhas):
        ponteiros[i + 1] += ponteiros[i]
    return CSR(
        linhas, colunas,
        tuple(v for _, _, v in ordenado),
        tuple(j for _, j, _ in ordenado),
        tuple(ponteiros),
    )


def gerar_csr(rng: random.Random, linhas: int, colunas: int, densidade: float) -> CSR:
    return coo_para_csr(linhas, colunas, gerar_coo(rng, linhas, colunas, densidade))
