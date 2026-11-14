"""Escalonamento por loteria (probabilístico) e stride (determinístico).

Loteria: o sorteio escolhe um bilhete; vence quem detém o intervalo que o contém.
O gerador de números é injetável para os testes serem reprodutíveis.

Stride: cada cliente tem `passo = GRANDE // bilhetes` e uma `passagem` acumulada;
roda sempre quem tem a menor passagem, que então avança em `passo`.
"""
from __future__ import annotations

from typing import Iterable, Iterator

GRANDE = 10_000


class Lcg:
    """Gerador congruente linear (parâmetros do glibc) para sorteios determinísticos."""

    def __init__(self, semente: int = 1) -> None:
        self.estado = semente % 2**31

    def proximo(self) -> int:
        self.estado = (1103515245 * self.estado + 12345) % 2**31
        return self.estado


class Loteria:
    def __init__(self) -> None:
        self.bilhetes: dict[str, int] = {}

    def adicionar(self, pid: str, bilhetes: int) -> None:
        if bilhetes <= 0:
            raise ValueError("bilhetes devem ser positivos")
        if pid in self.bilhetes:
            raise ValueError(f"pid duplicado: {pid}")
        self.bilhetes[pid] = bilhetes

    def remover(self, pid: str) -> None:
        del self.bilhetes[pid]

    @property
    def total(self) -> int:
        return sum(self.bilhetes.values())

    def vencedor(self, numero: int) -> str:
        """Mapeia um número sorteado ao dono do bilhete (em ordem de inserção)."""
        if not self.bilhetes:
            raise ValueError("sem processos")
        alvo = numero % self.total
        acumulado = 0
        for pid, qtd in self.bilhetes.items():
            acumulado += qtd
            if alvo < acumulado:
                return pid
        raise AssertionError("inalcançável")

    def sortear(self, numeros: Iterable[int]) -> list[str]:
        return [self.vencedor(n) for n in numeros]


class Stride:
    def __init__(self) -> None:
        self.passo: dict[str, int] = {}
        self.passagem: dict[str, int] = {}

    def adicionar(self, pid: str, bilhetes: int) -> None:
        if bilhetes <= 0 or bilhetes > GRANDE:
            raise ValueError("bilhetes fora de (0, GRANDE]")
        if pid in self.passo:
            raise ValueError(f"pid duplicado: {pid}")
        self.passo[pid] = GRANDE // bilhetes
        # quem entra tarde começa na menor passagem atual, sem monopolizar a CPU
        self.passagem[pid] = min(self.passagem.values(), default=0)

    def remover(self, pid: str) -> None:
        del self.passo[pid]
        del self.passagem[pid]

    def proximo(self) -> str:
        if not self.passo:
            raise ValueError("sem processos")
        pid = min(self.passo, key=lambda p: self.passagem[p])  # empate: ordem de inserção
        self.passagem[pid] += self.passo[pid]
        return pid

    def rodar(self, quanta: int) -> Iterator[str]:
        for _ in range(quanta):
            yield self.proximo()
