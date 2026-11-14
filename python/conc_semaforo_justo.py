"""Semáforo justo: os waiters são atendidos em ordem FIFO."""
from __future__ import annotations

import threading
from collections import deque


class SemaforoJusto:
    def __init__(self, valor: int = 1) -> None:
        if valor < 0:
            raise ValueError("valor deve ser >= 0")
        self._valor = valor
        self._lock = threading.Lock()
        self._espera: deque[threading.Event] = deque()

    @property
    def valor(self) -> int:
        with self._lock:
            return self._valor

    @property
    def aguardando(self) -> int:
        with self._lock:
            return len(self._espera)

    def adquirir(self, timeout: float | None = None) -> bool:
        with self._lock:
            if self._valor > 0 and not self._espera:
                self._valor -= 1
                return True
            evento = threading.Event()
            self._espera.append(evento)
        if evento.wait(timeout):
            return True
        with self._lock:
            if evento.is_set():  # liberado exatamente na corrida do timeout
                return True
            self._espera.remove(evento)
            return False

    def liberar(self) -> None:
        with self._lock:
            if self._espera:
                self._espera.popleft().set()  # repassa a permissão diretamente
            else:
                self._valor += 1

    def __enter__(self) -> "SemaforoJusto":
        self.adquirir()
        return self

    def __exit__(self, *exc: object) -> None:
        self.liberar()
