"""Árvore de decisão (Gini/entropia) com poda por profundidade e amostras mínimas."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass


def gini(rotulos: list) -> float:
    n = len(rotulos)
    if n == 0:
        return 0.0
    return 1.0 - sum((c / n) ** 2 for c in Counter(rotulos).values())


def entropia(rotulos: list) -> float:
    n = len(rotulos)
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in Counter(rotulos).values())


@dataclass
class No:
    rotulo: object = None
    atributo: int = -1
    limiar: float = 0.0
    esquerda: "No | None" = None
    direita: "No | None" = None

    @property
    def folha(self) -> bool:
        return self.esquerda is None


class ArvoreDecisao:
    def __init__(self, criterio: str = "gini", profundidade_max: int | None = None,
                 min_amostras: int = 2, atributos: list[int] | None = None) -> None:
        if criterio not in ("gini", "entropia"):
            raise ValueError("critério deve ser 'gini' ou 'entropia'")
        self.impureza = gini if criterio == "gini" else entropia
        self.profundidade_max = profundidade_max
        self.min_amostras = min_amostras
        self.atributos = atributos
        self.raiz: No | None = None

    def treinar(self, X: list[list[float]], y: list) -> "ArvoreDecisao":
        if not X or len(X) != len(y):
            raise ValueError("X e y devem ter o mesmo tamanho, não vazio")
        self.raiz = self._construir(X, y, 0)
        return self

    def _construir(self, X, y, prof) -> No:
        maioria = Counter(y).most_common(1)[0][0]
        if (len(set(y)) == 1 or len(y) < self.min_amostras
                or (self.profundidade_max is not None and prof >= self.profundidade_max)):
            return No(rotulo=maioria)
        melhor = self._melhor_corte(X, y)
        if melhor is None:
            return No(rotulo=maioria)
        a, lim = melhor
        esq = [i for i, x in enumerate(X) if x[a] <= lim]
        dir_ = [i for i, x in enumerate(X) if x[a] > lim]
        return No(
            rotulo=maioria, atributo=a, limiar=lim,
            esquerda=self._construir([X[i] for i in esq], [y[i] for i in esq], prof + 1),
            direita=self._construir([X[i] for i in dir_], [y[i] for i in dir_], prof + 1),
        )

    def _melhor_corte(self, X, y):
        base = self.impureza(y)
        melhor_ganho, melhor = 1e-12, None
        n = len(y)
        cols = self.atributos if self.atributos is not None else range(len(X[0]))
        for a in cols:
            valores = sorted(set(x[a] for x in X))
            for v1, v2 in zip(valores, valores[1:]):
                lim = (v1 + v2) / 2
                e = [y[i] for i in range(n) if X[i][a] <= lim]
                d = [y[i] for i in range(n) if X[i][a] > lim]
                ganho = base - (len(e) * self.impureza(e) + len(d) * self.impureza(d)) / n
                if ganho > melhor_ganho:
                    melhor_ganho, melhor = ganho, (a, lim)
        return melhor

    def prever_um(self, x: list[float]):
        if self.raiz is None:
            raise RuntimeError("árvore não treinada")
        no = self.raiz
        while not no.folha:
            no = no.esquerda if x[no.atributo] <= no.limiar else no.direita
        return no.rotulo

    def prever(self, X: list[list[float]]) -> list:
        return [self.prever_um(x) for x in X]

    def profundidade(self) -> int:
        def h(no):
            return 0 if no is None or no.folha else 1 + max(h(no.esquerda), h(no.direita))
        return h(self.raiz)
