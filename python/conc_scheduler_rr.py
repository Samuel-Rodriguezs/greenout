"""Scheduler cooperativo round-robin com quantum (em passos) e prioridades opcionais."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Generator, Iterator


@dataclass
class Processo:
    pid: int
    nome: str
    gen: Generator
    passos: int = 0
    terminado: bool = False
    resultado: Any = None
    quanta_usados: int = 0
    historico: list[int] = field(default_factory=list)


class SchedulerRR:
    """Cada `yield` do gerador é um passo; após `quantum` passos o processo é preemptado."""

    def __init__(self, quantum: int = 1) -> None:
        if quantum < 1:
            raise ValueError("quantum deve ser >= 1")
        self.quantum = quantum
        self._fila: deque[Processo] = deque()
        self._proximo_pid = 1
        self.processos: dict[int, Processo] = {}
        self.ordem_execucao: list[int] = []  # pid por fatia de CPU

    def criar(self, gen: Generator, nome: str = "") -> int:
        p = Processo(self._proximo_pid, nome or f"p{self._proximo_pid}", gen)
        self._proximo_pid += 1
        self.processos[p.pid] = p
        self._fila.append(p)
        return p.pid

    def _fatia(self, p: Processo) -> None:
        self.ordem_execucao.append(p.pid)
        p.quanta_usados += 1
        for _ in range(self.quantum):
            try:
                next(p.gen)
                p.passos += 1
            except StopIteration as fim:
                p.terminado, p.resultado = True, fim.value
                return
        self._fila.append(p)

    def passo(self) -> bool:
        """Executa uma fatia; retorna False se não há mais processos."""
        if not self._fila:
            return False
        self._fatia(self._fila.popleft())
        return True

    def executar(self, max_fatias: int = 100_000) -> int:
        n = 0
        while n < max_fatias and self.passo():
            n += 1
        return n

    def __iter__(self) -> Iterator[Processo]:
        return iter(self.processos.values())
