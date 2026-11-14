"""Gerador congruencial linear (LCG) pseudoaleatório."""
from typing import List


class LCG:
    """x_{n+1} = (a*x_n + c) mod m; parâmetros padrão de Numerical Recipes."""

    def __init__(self, semente: int = 1, a: int = 1664525, c: int = 1013904223,
                 m: int = 2 ** 32) -> None:
        if m <= 0:
            raise ValueError("m deve ser positivo")
        self.a, self.c, self.m = a, c, m
        self.estado = semente % m

    def proximo(self) -> int:
        self.estado = (self.a * self.estado + self.c) % self.m
        return self.estado

    def aleatorio(self) -> float:
        """Float em [0, 1)."""
        return self.proximo() / self.m

    def inteiro(self, a: int, b: int) -> int:
        """Inteiro em [a, b]."""
        if a > b:
            raise ValueError("a deve ser <= b")
        return a + self.proximo() % (b - a + 1)

    def lista(self, n: int) -> List[float]:
        return [self.aleatorio() for _ in range(n)]
