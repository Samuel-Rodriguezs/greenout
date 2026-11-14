"""Lock de leitores-escritores com preferência para escritores (sem inanição)."""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator


class LockLeitoresEscritores:
    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._leitores = 0
        self._escritor_ativo = False
        self._escritores_esperando = 0

    @property
    def leitores(self) -> int:
        with self._cond:
            return self._leitores

    def adquirir_leitura(self) -> None:
        with self._cond:
            self._cond.wait_for(
                lambda: not self._escritor_ativo and self._escritores_esperando == 0
            )
            self._leitores += 1

    def liberar_leitura(self) -> None:
        with self._cond:
            if self._leitores == 0:
                raise RuntimeError("nenhuma leitura ativa")
            self._leitores -= 1
            if self._leitores == 0:
                self._cond.notify_all()

    def adquirir_escrita(self) -> None:
        with self._cond:
            self._escritores_esperando += 1
            try:
                self._cond.wait_for(
                    lambda: not self._escritor_ativo and self._leitores == 0
                )
            finally:
                self._escritores_esperando -= 1
            self._escritor_ativo = True

    def liberar_escrita(self) -> None:
        with self._cond:
            if not self._escritor_ativo:
                raise RuntimeError("nenhuma escrita ativa")
            self._escritor_ativo = False
            self._cond.notify_all()

    @contextmanager
    def leitura(self) -> Iterator[None]:
        self.adquirir_leitura()
        try:
            yield
        finally:
            self.liberar_leitura()

    @contextmanager
    def escrita(self) -> Iterator[None]:
        self.adquirir_escrita()
        try:
            yield
        finally:
            self.liberar_escrita()
