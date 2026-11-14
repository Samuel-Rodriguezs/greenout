"""Fila limitada (bounded buffer) com Condition: produtor/consumidor."""
from __future__ import annotations

import threading
from collections import deque
from typing import Any


class FilaLimitada:
    def __init__(self, capacidade: int) -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self.capacidade = capacidade
        self._itens: deque[Any] = deque()
        self._lock = threading.Lock()
        self._nao_cheia = threading.Condition(self._lock)
        self._nao_vazia = threading.Condition(self._lock)
        self._fechada = False

    def __len__(self) -> int:
        with self._lock:
            return len(self._itens)

    def colocar(self, item: Any, timeout: float | None = None) -> None:
        with self._nao_cheia:
            if self._fechada:
                raise RuntimeError("fila fechada")
            ok = self._nao_cheia.wait_for(
                lambda: len(self._itens) < self.capacidade or self._fechada, timeout
            )
            if not ok:
                raise TimeoutError("fila cheia")
            if self._fechada:
                raise RuntimeError("fila fechada")
            self._itens.append(item)
            self._nao_vazia.notify()

    def retirar(self, timeout: float | None = None) -> Any:
        """Retira um item; levanta EOFError se fechada e vazia."""
        with self._nao_vazia:
            ok = self._nao_vazia.wait_for(
                lambda: self._itens or self._fechada, timeout
            )
            if not ok:
                raise TimeoutError("fila vazia")
            if not self._itens:
                raise EOFError("fila fechada e vazia")
            item = self._itens.popleft()
            self._nao_cheia.notify()
            return item

    def fechar(self) -> None:
        with self._lock:
            self._fechada = True
            self._nao_cheia.notify_all()
            self._nao_vazia.notify_all()
