"""Rate limiter assíncrono (token bucket) com relógio e sleep injetáveis."""
from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable


class RateLimiter:
    """Permite `taxa` tokens por segundo, com rajada máxima `capacidade`."""

    def __init__(
        self,
        taxa: float,
        capacidade: int = 1,
        relogio: Callable[[], float] = time.monotonic,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if taxa <= 0 or capacidade < 1:
            raise ValueError("taxa deve ser > 0 e capacidade >= 1")
        self.taxa = taxa
        self.capacidade = capacidade
        self._relogio = relogio
        self._dormir = dormir
        self._tokens = float(capacidade)
        self._ultimo = relogio()
        self._lock: asyncio.Lock | None = None

    def _repor(self) -> None:
        agora = self._relogio()
        self._tokens = min(
            float(self.capacidade), self._tokens + (agora - self._ultimo) * self.taxa
        )
        self._ultimo = agora

    def tentar(self, n: int = 1) -> bool:
        """Consome n tokens sem esperar; False se insuficientes."""
        self._repor()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    def tempo_ate_disponivel(self, n: int = 1) -> float:
        self._repor()
        falta = n - self._tokens
        return max(0.0, falta / self.taxa)

    async def adquirir(self, n: int = 1) -> float:
        """Espera até haver n tokens; devolve o total de segundos esperado."""
        if n > self.capacidade:
            raise ValueError("n excede a capacidade")
        if self._lock is None:
            self._lock = asyncio.Lock()
        esperado = 0.0
        async with self._lock:  # preserva a ordem de chegada
            while not self.tentar(n):
                espera = self.tempo_ate_disponivel(n)
                await self._dormir(espera)
                esperado += espera
        return esperado
