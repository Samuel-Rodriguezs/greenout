"""Event loop mínimo: corrotinas por gerador (yield) com tempo virtual.

Uma tarefa é um gerador que faz `yield` de comandos:
  - `Dormir(t)`: suspende por t unidades de tempo virtual;
  - `Esperar(tarefa)`: suspende até a outra tarefa terminar e recebe o resultado;
  - `None`: cede a vez (yield simples).
"""
from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass
from typing import Any, Generator


@dataclass(frozen=True)
class Dormir:
    tempo: float


@dataclass(frozen=True)
class Esperar:
    tarefa: "Tarefa"


class Tarefa:
    def __init__(self, gen: Generator, nome: str) -> None:
        self.gen = gen
        self.nome = nome
        self.pronta = False
        self.resultado: Any = None
        self.erro: BaseException | None = None
        self.valor_envio: Any = None
        self.esperando: list["Tarefa"] = []


class EventLoop:
    def __init__(self) -> None:
        self.agora = 0.0
        self._prontas: deque[Tarefa] = deque()
        self._dormindo: list[tuple[float, int, Tarefa]] = []
        self._seq = itertools.count()

    def criar_tarefa(self, gen: Generator, nome: str = "") -> Tarefa:
        t = Tarefa(gen, nome or f"tarefa-{next(self._seq)}")
        self._prontas.append(t)
        return t

    def _concluir(self, t: Tarefa, resultado: Any, erro: BaseException | None) -> None:
        t.pronta, t.resultado, t.erro = True, resultado, erro
        for w in t.esperando:
            w.valor_envio = t
            self._prontas.append(w)
        t.esperando = []

    def _passo(self, t: Tarefa) -> None:
        try:
            cmd = t.gen.send(t.valor_envio)
        except StopIteration as fim:
            self._concluir(t, fim.value, None)
            return
        except BaseException as exc:  # noqa: BLE001
            self._concluir(t, None, exc)
            return
        t.valor_envio = None
        if isinstance(cmd, Dormir):
            heapq.heappush(self._dormindo, (self.agora + cmd.tempo, next(self._seq), t))
        elif isinstance(cmd, Esperar):
            alvo = cmd.tarefa
            if alvo.pronta:
                t.valor_envio = alvo
                self._prontas.append(t)
            else:
                alvo.esperando.append(t)
        else:
            self._prontas.append(t)

    def executar(self) -> float:
        """Roda até não restar trabalho; devolve o tempo virtual final."""
        while self._prontas or self._dormindo:
            if not self._prontas:
                self.agora, _, t = heapq.heappop(self._dormindo)
                self._prontas.append(t)
                while self._dormindo and self._dormindo[0][0] <= self.agora:
                    self._prontas.append(heapq.heappop(self._dormindo)[2])
            self._passo(self._prontas.popleft())
        return self.agora
