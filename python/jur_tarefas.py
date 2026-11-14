"""Fila de tarefas do escritório com prioridade, prazo e responsável."""
from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass
from datetime import date
from enum import IntEnum


class Prioridade(IntEnum):
    URGENTE = 0
    ALTA = 1
    NORMAL = 2
    BAIXA = 3


@dataclass(frozen=True)
class Tarefa:
    id: int
    titulo: str
    prioridade: Prioridade
    responsavel: str
    prazo: date | None = None


class FilaTarefas:
    """Ordem: prioridade, prazo mais próximo (sem prazo por último), depois ordem de chegada."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, date, int, Tarefa]] = []
        self._cont = itertools.count(1)
        self._canceladas: set[int] = set()

    def adicionar(self, titulo: str, prioridade: Prioridade = Prioridade.NORMAL, responsavel: str = "",
                  prazo: date | None = None) -> Tarefa:
        if not titulo.strip():
            raise ValueError("título obrigatório")
        n = next(self._cont)
        t = Tarefa(n, titulo.strip(), prioridade, responsavel, prazo)
        heapq.heappush(self._heap, (int(prioridade), prazo or date.max, n, t))
        return t

    def cancelar(self, id: int) -> None:
        if not any(t.id == id for *_, t in self._heap) or id in self._canceladas:
            raise KeyError(f"tarefa {id} não está na fila")
        self._canceladas.add(id)

    def _limpar_topo(self) -> None:
        while self._heap and self._heap[0][3].id in self._canceladas:
            heapq.heappop(self._heap)

    def proxima(self, responsavel: str | None = None) -> Tarefa | None:
        """Retira a próxima tarefa (opcionalmente só de um responsável)."""
        self._limpar_topo()
        if responsavel is None:
            return heapq.heappop(self._heap)[3] if self._heap else None
        for item in sorted(self._heap):
            t = item[3]
            if t.id not in self._canceladas and t.responsavel == responsavel:
                self._heap.remove(item)
                heapq.heapify(self._heap)
                return t
        return None

    def espiar(self) -> Tarefa | None:
        self._limpar_topo()
        return self._heap[0][3] if self._heap else None

    def pendentes(self) -> list[Tarefa]:
        return [i[3] for i in sorted(self._heap) if i[3].id not in self._canceladas]

    def atrasadas(self, hoje: date) -> list[Tarefa]:
        return [t for t in self.pendentes() if t.prazo is not None and t.prazo < hoje]

    def __len__(self) -> int:
        return len(self.pendentes())
