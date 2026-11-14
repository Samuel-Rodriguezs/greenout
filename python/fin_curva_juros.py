"""Curva de juros: interpolação de taxas spot, fatores de desconto e forwards."""
from __future__ import annotations

import math
from bisect import bisect_left


class CurvaJuros:
    """Taxas spot anuais (capitalização composta) por prazo em anos.

    Fora do intervalo de vértices a taxa é mantida constante (extrapolação plana)."""

    def __init__(self, prazos: list[float], taxas: list[float]) -> None:
        if len(prazos) != len(taxas) or not prazos:
            raise ValueError("prazos e taxas devem ter o mesmo tamanho (> 0)")
        if any(p <= 0 for p in prazos):
            raise ValueError("prazos devem ser positivos")
        pares = sorted(zip(prazos, taxas))
        if len({p for p, _ in pares}) != len(pares):
            raise ValueError("prazos repetidos")
        self.prazos = [p for p, _ in pares]
        self.taxas = [t for _, t in pares]

    def _vizinhos(self, t: float) -> tuple[int, int] | None:
        if t <= self.prazos[0] or t >= self.prazos[-1]:
            return None
        j = bisect_left(self.prazos, t)
        return j - 1, j

    def taxa_linear(self, t: float) -> float:
        """Interpolação linear na taxa."""
        if t <= 0:
            raise ValueError("prazo deve ser positivo")
        viz = self._vizinhos(t)
        if viz is None:
            return self.taxas[0] if t <= self.prazos[0] else self.taxas[-1]
        i, j = viz
        w = (t - self.prazos[i]) / (self.prazos[j] - self.prazos[i])
        return self.taxas[i] + w * (self.taxas[j] - self.taxas[i])

    def taxa_flat_forward(self, t: float) -> float:
        """Interpolação linear do log do fator de capitalização (flat forward)."""
        if t <= 0:
            raise ValueError("prazo deve ser positivo")
        viz = self._vizinhos(t)
        if viz is None:
            return self.taxas[0] if t <= self.prazos[0] else self.taxas[-1]
        i, j = viz
        li = self.prazos[i] * math.log(1 + self.taxas[i])
        lj = self.prazos[j] * math.log(1 + self.taxas[j])
        w = (t - self.prazos[i]) / (self.prazos[j] - self.prazos[i])
        return math.exp((li + w * (lj - li)) / t) - 1

    def fator_desconto(self, t: float, metodo: str = "linear") -> float:
        taxa = self.taxa_linear(t) if metodo == "linear" else self.taxa_flat_forward(t)
        return 1 / (1 + taxa) ** t

    def taxa_forward(self, t1: float, t2: float, metodo: str = "linear") -> float:
        """Taxa anual implícita entre t1 e t2: ((1+s2)^t2 / (1+s1)^t1)^(1/(t2-t1)) - 1."""
        if not 0 < t1 < t2:
            raise ValueError("é necessário 0 < t1 < t2")
        return (self.fator_desconto(t1, metodo) / self.fator_desconto(t2, metodo)) ** (
            1 / (t2 - t1)
        ) - 1
