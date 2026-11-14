"""Rede neural de 2 camadas (entrada -> oculta -> saída) com backprop manual."""
from __future__ import annotations

import math
import random


def _sig(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(min(z, 500), -500)))


class RedeNeural:
    def __init__(self, entradas: int = 2, ocultos: int = 4, seed: int = 1, taxa: float = 0.5) -> None:
        rng = random.Random(seed)
        self.taxa = taxa
        self.w1 = [[rng.uniform(-1, 1) for _ in range(entradas)] for _ in range(ocultos)]
        self.b1 = [0.0] * ocultos
        self.w2 = [rng.uniform(-1, 1) for _ in range(ocultos)]
        self.b2 = 0.0

    def frente(self, x: list[float]) -> tuple[list[float], float]:
        h = [_sig(b + sum(w * v for w, v in zip(lin, x))) for lin, b in zip(self.w1, self.b1)]
        y = _sig(self.b2 + sum(w * a for w, a in zip(self.w2, h)))
        return h, y

    def prever(self, x: list[float]) -> float:
        return self.frente(x)[1]

    def passo(self, x: list[float], alvo: float) -> float:
        """Um passo de SGD com erro quadrático; retorna o erro antes da atualização."""
        h, y = self.frente(x)
        d_saida = (y - alvo) * y * (1 - y)
        d_oculta = [d_saida * self.w2[j] * h[j] * (1 - h[j]) for j in range(len(h))]
        for j in range(len(h)):
            self.w2[j] -= self.taxa * d_saida * h[j]
            for i in range(len(x)):
                self.w1[j][i] -= self.taxa * d_oculta[j] * x[i]
            self.b1[j] -= self.taxa * d_oculta[j]
        self.b2 -= self.taxa * d_saida
        return 0.5 * (y - alvo) ** 2

    def treinar(self, X: list[list[float]], y: list[float], epocas: int = 3000) -> float:
        erro = 0.0
        for _ in range(epocas):
            erro = sum(self.passo(x, a) for x, a in zip(X, y))
        return erro


XOR_X = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
XOR_Y = [0.0, 1.0, 1.0, 0.0]


def treinar_xor(seed: int = 1, epocas: int = 3000) -> RedeNeural:
    rede = RedeNeural(seed=seed)
    rede.treinar(XOR_X, XOR_Y, epocas)
    return rede
