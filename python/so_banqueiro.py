"""Algoritmo do banqueiro (Dijkstra) para evitar deadlock.

Matrizes: `alocado[i][j]` (recursos j em posse do processo i), `maximo[i][j]`
(demanda máxima declarada) e `disponivel[j]`. Um estado é seguro se existe uma
sequência em que todo processo consegue terminar com os recursos disponíveis
mais os liberados pelos anteriores.
"""
from __future__ import annotations

from typing import Optional

CONCEDIDO = "concedido"
ESPERA = "espera"
INSEGURO = "inseguro"


class Banqueiro:
    def __init__(
        self,
        disponivel: list[int],
        alocado: list[list[int]],
        maximo: list[list[int]],
    ) -> None:
        m = len(disponivel)
        if len(alocado) != len(maximo) or any(len(l) != m for l in alocado + maximo):
            raise ValueError("dimensões inconsistentes")
        if any(a < 0 for a in disponivel) or any(x < 0 for l in alocado + maximo for x in l):
            raise ValueError("valores negativos")
        if any(a > mx for la, lm in zip(alocado, maximo) for a, mx in zip(la, lm)):
            raise ValueError("alocação excede o máximo declarado")
        self.disponivel = list(disponivel)
        self.alocado = [list(l) for l in alocado]
        self.maximo = [list(l) for l in maximo]

    @property
    def n(self) -> int:
        return len(self.alocado)

    def necessidade(self, i: int) -> list[int]:
        return [m - a for m, a in zip(self.maximo[i], self.alocado[i])]

    def sequencia_segura(self) -> Optional[list[int]]:
        """Sequência segura (varredura em ordem de índice) ou None se inseguro."""
        trabalho = list(self.disponivel)
        terminou = [False] * self.n
        sequencia: list[int] = []
        progresso = True
        while progresso:
            progresso = False
            for i in range(self.n):
                if terminou[i]:
                    continue
                if all(nec <= t for nec, t in zip(self.necessidade(i), trabalho)):
                    trabalho = [t + a for t, a in zip(trabalho, self.alocado[i])]
                    terminou[i] = True
                    sequencia.append(i)
                    progresso = True
        return sequencia if all(terminou) else None

    def seguro(self) -> bool:
        return self.sequencia_segura() is not None

    def requisitar(self, i: int, pedido: list[int]) -> str:
        """Concede só se o pedido é válido, há recursos e o estado resultante é seguro."""
        if len(pedido) != len(self.disponivel) or any(p < 0 for p in pedido):
            raise ValueError("pedido inválido")
        if any(p > nec for p, nec in zip(pedido, self.necessidade(i))):
            raise ValueError("processo excedeu seu máximo declarado")
        if any(p > d for p, d in zip(pedido, self.disponivel)):
            return ESPERA
        self.disponivel = [d - p for d, p in zip(self.disponivel, pedido)]
        self.alocado[i] = [a + p for a, p in zip(self.alocado[i], pedido)]
        if self.seguro():
            return CONCEDIDO
        self.disponivel = [d + p for d, p in zip(self.disponivel, pedido)]  # desfaz
        self.alocado[i] = [a - p for a, p in zip(self.alocado[i], pedido)]
        return INSEGURO

    def liberar(self, i: int) -> None:
        """Processo termina e devolve tudo que possui."""
        self.disponivel = [d + a for d, a in zip(self.disponivel, self.alocado[i])]
        self.alocado[i] = [0] * len(self.disponivel)
        self.maximo[i] = [0] * len(self.disponivel)
