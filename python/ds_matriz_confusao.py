"""Matriz de confusão e métricas de classificação."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Sequence


@dataclass
class MatrizConfusao:
    rotulos: list[Hashable]
    matriz: list[list[int]]  # linhas = real, colunas = previsto

    @property
    def total(self) -> int:
        return sum(sum(l) for l in self.matriz)

    def _idx(self, rotulo: Hashable) -> int:
        return self.rotulos.index(rotulo)

    def vp(self, rotulo: Hashable) -> int:
        i = self._idx(rotulo)
        return self.matriz[i][i]

    def fp(self, rotulo: Hashable) -> int:
        i = self._idx(rotulo)
        return sum(l[i] for l in self.matriz) - self.matriz[i][i]

    def fn(self, rotulo: Hashable) -> int:
        i = self._idx(rotulo)
        return sum(self.matriz[i]) - self.matriz[i][i]

    def vn(self, rotulo: Hashable) -> int:
        return self.total - self.vp(rotulo) - self.fp(rotulo) - self.fn(rotulo)

    def acuracia(self) -> float:
        return sum(self.matriz[i][i] for i in range(len(self.rotulos))) / self.total

    def precisao(self, rotulo: Hashable) -> float:
        d = self.vp(rotulo) + self.fp(rotulo)
        return self.vp(rotulo) / d if d else 0.0

    def revocacao(self, rotulo: Hashable) -> float:
        d = self.vp(rotulo) + self.fn(rotulo)
        return self.vp(rotulo) / d if d else 0.0

    def f1(self, rotulo: Hashable) -> float:
        p, r = self.precisao(rotulo), self.revocacao(rotulo)
        return 2 * p * r / (p + r) if p + r else 0.0

    def f1_macro(self) -> float:
        return sum(self.f1(r) for r in self.rotulos) / len(self.rotulos)

    def kappa(self) -> float:
        """Kappa de Cohen."""
        n = self.total
        po = self.acuracia()
        pe = sum(
            sum(self.matriz[i]) * sum(l[i] for l in self.matriz) for i in range(len(self.rotulos))
        ) / (n * n)
        return 1.0 if pe == 1 else (po - pe) / (1 - pe)

    def formatar(self) -> str:
        larg = max(len(str(r)) for r in self.rotulos + [max((v for l in self.matriz for v in l), default=0)]) + 1
        cab = " " * larg + "".join(str(r).rjust(larg) for r in self.rotulos)
        linhas = [cab]
        for r, l in zip(self.rotulos, self.matriz):
            linhas.append(str(r).rjust(larg) + "".join(str(v).rjust(larg) for v in l))
        return "\n".join(linhas)


def matriz_confusao(
    reais: Sequence[Hashable], previstos: Sequence[Hashable], rotulos: Sequence[Hashable] | None = None
) -> MatrizConfusao:
    if len(reais) != len(previstos) or not reais:
        raise ValueError("listas devem ter o mesmo tamanho (não vazio)")
    if rotulos is None:
        rotulos = sorted(set(reais) | set(previstos), key=lambda x: (str(type(x)), x))
    rot = list(rotulos)
    pos = {r: i for i, r in enumerate(rot)}
    m = [[0] * len(rot) for _ in rot]
    for a, b in zip(reais, previstos):
        if a not in pos or b not in pos:
            raise ValueError(f"rótulo fora da lista: {a if a not in pos else b!r}")
        m[pos[a]][pos[b]] += 1
    return MatrizConfusao(rot, m)
