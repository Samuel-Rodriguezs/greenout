"""Barreira reutilizável (cíclica) implementada com Condition e geração."""
from __future__ import annotations

import threading
from typing import Callable


class BarreiraReutilizavel:
    def __init__(self, partes: int, acao: Callable[[], None] | None = None) -> None:
        if partes < 1:
            raise ValueError("partes deve ser >= 1")
        self.partes = partes
        self._acao = acao
        self._cond = threading.Condition()
        self._chegadas = 0
        self._geracao = 0

    def esperar(self, timeout: float | None = None) -> int:
        """Bloqueia até todas as partes chegarem. Retorna o índice de chegada."""
        with self._cond:
            geracao = self._geracao
            indice = self._chegadas
            self._chegadas += 1
            if self._chegadas == self.partes:
                if self._acao is not None:
                    self._acao()
                self._chegadas = 0
                self._geracao += 1
                self._cond.notify_all()
                return indice
            if not self._cond.wait_for(lambda: geracao != self._geracao, timeout):
                self._chegadas -= 1
                raise TimeoutError("barreira não completada")
            return indice

    @property
    def geracao(self) -> int:
        with self._cond:
            return self._geracao
