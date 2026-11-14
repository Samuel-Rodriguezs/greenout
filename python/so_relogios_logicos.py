"""Relógios lógicos: Lamport e vetorial, rodando juntos sobre os mesmos eventos.

Lamport: local/envio incrementam; recebimento faz max(local, msg) + 1. Garante
a -> b implica L(a) < L(b), mas não o inverso. O relógio vetorial captura
causalidade exata: dois eventos são concorrentes se nenhum vetor domina o outro.
"""
from __future__ import annotations

from dataclasses import dataclass

ANTES = "antes"
DEPOIS = "depois"
CONCORRENTE = "concorrente"
IGUAL = "igual"


def comparar_vetores(a: tuple[int, ...], b: tuple[int, ...]) -> str:
    if len(a) != len(b):
        raise ValueError("vetores de tamanhos diferentes")
    if a == b:
        return IGUAL
    if all(x <= y for x, y in zip(a, b)):
        return ANTES
    if all(x >= y for x, y in zip(a, b)):
        return DEPOIS
    return CONCORRENTE


@dataclass(frozen=True)
class Evento:
    indice: int
    proc: int
    tipo: str  # "local", "envio" ou "recebimento"
    lamport: int
    vetor: tuple[int, ...]
    msg: str = ""


class Simulacao:
    def __init__(self, n: int) -> None:
        if n <= 0:
            raise ValueError("n deve ser positivo")
        self.n = n
        self.lamport = [0] * n
        self.vetor = [[0] * n for _ in range(n)]
        self.eventos: list[Evento] = []
        self._em_transito: dict[str, tuple[int, tuple[int, ...]]] = {}

    def _registrar(self, p: int, tipo: str, msg: str = "") -> Evento:
        ev = Evento(len(self.eventos), p, tipo, self.lamport[p], tuple(self.vetor[p]), msg)
        self.eventos.append(ev)
        return ev

    def _checar(self, p: int) -> None:
        if not 0 <= p < self.n:
            raise ValueError(f"processo inexistente: {p}")

    def local(self, p: int) -> Evento:
        self._checar(p)
        self.lamport[p] += 1
        self.vetor[p][p] += 1
        return self._registrar(p, "local")

    def envia(self, p: int, msg: str) -> Evento:
        self._checar(p)
        if msg in self._em_transito:
            raise ValueError(f"mensagem já enviada: {msg}")
        self.lamport[p] += 1
        self.vetor[p][p] += 1
        self._em_transito[msg] = (self.lamport[p], tuple(self.vetor[p]))
        return self._registrar(p, "envio", msg)

    def recebe(self, p: int, msg: str) -> Evento:
        self._checar(p)
        if msg not in self._em_transito:
            raise ValueError(f"mensagem desconhecida: {msg}")
        ts, vt = self._em_transito[msg]
        self.lamport[p] = max(self.lamport[p], ts) + 1
        self.vetor[p] = [max(a, b) for a, b in zip(self.vetor[p], vt)]
        self.vetor[p][p] += 1
        return self._registrar(p, "recebimento", msg)

    def relacao(self, a: Evento, b: Evento) -> str:
        """Relação causal de a em relação a b, pelos vetores."""
        return comparar_vetores(a.vetor, b.vetor)

    def ordem_total(self) -> list[Evento]:
        """Ordem total de Lamport: (timestamp, processo) desempata eventos concorrentes."""
        return sorted(self.eventos, key=lambda e: (e.lamport, e.proc))
