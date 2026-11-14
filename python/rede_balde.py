"""Modeladores de tráfego: token bucket e leaky bucket (relógio injetável)."""
from __future__ import annotations

from typing import Callable


class TokenBucket:
    """Permite rajadas até `capacidade`; taxa média `taxa` tokens/s."""

    def __init__(self, taxa: float, capacidade: float,
                 relogio: Callable[[], float] | None = None) -> None:
        if taxa <= 0 or capacidade <= 0:
            raise ValueError("taxa e capacidade devem ser positivas")
        self.taxa, self.capacidade = taxa, capacidade
        self._relogio = relogio or (lambda: 0.0)
        self._tokens = float(capacidade)
        self._ultimo = self._relogio()

    def _reabastecer(self) -> None:
        agora = self._relogio()
        self._tokens = min(self.capacidade, self._tokens + (agora - self._ultimo) * self.taxa)
        self._ultimo = agora

    @property
    def tokens(self) -> float:
        self._reabastecer()
        return self._tokens

    def consumir(self, n: float = 1.0) -> bool:
        """True se havia tokens (pacote conforme); False caso contrário (sem consumir)."""
        if n > self.capacidade:
            return False
        self._reabastecer()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    def espera(self, n: float = 1.0) -> float:
        """Segundos até haver `n` tokens (0 se já há)."""
        if n > self.capacidade:
            raise ValueError("pedido maior que a capacidade")
        self._reabastecer()
        return max(0.0, (n - self._tokens) / self.taxa)


class LeakyBucket:
    """Fila de capacidade fixa que escoa a taxa constante; excedente é descartado."""

    def __init__(self, taxa: float, capacidade: float,
                 relogio: Callable[[], float] | None = None) -> None:
        if taxa <= 0 or capacidade <= 0:
            raise ValueError("taxa e capacidade devem ser positivas")
        self.taxa, self.capacidade = taxa, capacidade
        self._relogio = relogio or (lambda: 0.0)
        self._nivel = 0.0
        self._ultimo = self._relogio()

    def _escoar(self) -> None:
        agora = self._relogio()
        self._nivel = max(0.0, self._nivel - (agora - self._ultimo) * self.taxa)
        self._ultimo = agora

    @property
    def nivel(self) -> float:
        self._escoar()
        return self._nivel

    def adicionar(self, n: float = 1.0) -> bool:
        """True se coube no balde; False se transbordaria (pacote descartado)."""
        self._escoar()
        if self._nivel + n > self.capacidade:
            return False
        self._nivel += n
        return True

    def atraso(self) -> float:
        """Tempo de permanência de um pacote novo no fim da fila."""
        return self.nivel / self.taxa
