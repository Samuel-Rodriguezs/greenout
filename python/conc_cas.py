"""Contador atômico com compare-and-swap simulado (primitiva protegida por lock)."""
from __future__ import annotations

import threading
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class ReferenciaAtomica(Generic[T]):
    """Simula a instrução CAS: troca somente se o valor atual for o esperado."""

    def __init__(self, valor: T) -> None:
        self._valor = valor
        self._lock = threading.Lock()  # faz o papel do hardware
        self.falhas_cas = 0

    def obter(self) -> T:
        return self._valor

    def comparar_e_trocar(self, esperado: T, novo: T) -> bool:
        with self._lock:
            if self._valor == esperado:
                self._valor = novo
                return True
            self.falhas_cas += 1
            return False

    def atualizar(self, fn: Callable[[T], T]) -> T:
        """Laço CAS clássico: lê, calcula, tenta trocar; repete se houve corrida."""
        while True:
            antigo = self._valor
            novo = fn(antigo)
            if self.comparar_e_trocar(antigo, novo):
                return novo


class ContadorAtomico:
    def __init__(self, inicial: int = 0) -> None:
        self._ref: ReferenciaAtomica[int] = ReferenciaAtomica(inicial)

    @property
    def valor(self) -> int:
        return self._ref.obter()

    @property
    def falhas_cas(self) -> int:
        return self._ref.falhas_cas

    def incrementar(self, delta: int = 1) -> int:
        return self._ref.atualizar(lambda v: v + delta)

    def decrementar(self, delta: int = 1) -> int:
        return self.incrementar(-delta)

    def obter_e_incrementar(self, delta: int = 1) -> int:
        return self._ref.atualizar(lambda v: v + delta) - delta

    def comparar_e_definir(self, esperado: int, novo: int) -> bool:
        return self._ref.comparar_e_trocar(esperado, novo)

    def maximo(self, candidato: int) -> int:
        return self._ref.atualizar(lambda v: max(v, candidato))
