"""Semáforo de cruzamento: duas vias com fases verde/amarelo/vermelho e fila de carros."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Fases:
    verde: int = 6
    amarelo: int = 2
    todo_vermelho: int = 1


class Cruzamento:
    """Via 'NS' e via 'LO'. Em cada instante no máximo uma via pode ter verde/amarelo."""

    def __init__(self, fases: Fases | None = None, prob_chegada: float = 0.3,
                 rng: random.Random | None = None) -> None:
        self.fases = fases or Fases()
        self.prob = prob_chegada
        self.rng = rng or random.Random()
        self.filas = {"NS": 0, "LO": 0}
        self.passaram = {"NS": 0, "LO": 0}
        self.tempo = 0
        self._ciclo = [("NS", "verde", self.fases.verde), ("NS", "amarelo", self.fases.amarelo),
                       (None, "vermelho", self.fases.todo_vermelho),
                       ("LO", "verde", self.fases.verde), ("LO", "amarelo", self.fases.amarelo),
                       (None, "vermelho", self.fases.todo_vermelho)]
        self.duracao_ciclo = sum(d for _, _, d in self._ciclo)

    def estado(self, t: int | None = None) -> dict[str, str]:
        t = (self.tempo if t is None else t) % self.duracao_ciclo
        for via, cor, dur in self._ciclo:
            if t < dur:
                return {v: (cor if v == via else "vermelho") for v in ("NS", "LO")}
            t -= dur
        raise AssertionError("inalcançável")

    def passo(self) -> None:
        est = self.estado()
        for via in ("NS", "LO"):
            if self.rng.random() < self.prob:
                self.filas[via] += 1
            if est[via] == "verde" and self.filas[via]:
                self.filas[via] -= 1
                self.passaram[via] += 1
        self.tempo += 1

    def executar(self, n: int) -> None:
        for _ in range(n):
            self.passo()
