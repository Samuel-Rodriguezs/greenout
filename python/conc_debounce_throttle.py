"""Debounce e throttle com relógio injetável (modelo orientado a ticks)."""
from __future__ import annotations

import time
from typing import Any, Callable


class Debounce:
    """Agenda a execução para `espera` s após a última chamada.

    Sem threads: o dono chama `verificar()` periodicamente (ou o relógio avança nos testes).
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        espera: float,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        if espera < 0:
            raise ValueError("espera deve ser >= 0")
        self._fn = fn
        self._espera = espera
        self._relogio = relogio
        self._args: tuple | None = None
        self._kwargs: dict = {}
        self._vence_em = 0.0

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self._args, self._kwargs = args, kwargs
        self._vence_em = self._relogio() + self._espera

    @property
    def pendente(self) -> bool:
        return self._args is not None

    def verificar(self) -> bool:
        """Dispara se o prazo venceu; retorna True se executou."""
        if self._args is None or self._relogio() < self._vence_em:
            return False
        args, kwargs, self._args = self._args, self._kwargs, None
        self._fn(*args, **kwargs)
        return True

    def cancelar(self) -> None:
        self._args = None

    def descarregar(self) -> bool:
        """Executa imediatamente a chamada pendente (flush)."""
        if self._args is None:
            return False
        self._vence_em = 0.0
        return self.verificar()


class Throttle:
    """Executa no máximo uma vez por `intervalo`; com `final=True` guarda a última chamada
    ignorada para executá-la quando o intervalo terminar (trailing edge)."""

    def __init__(
        self,
        fn: Callable[..., Any],
        intervalo: float,
        final: bool = False,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        if intervalo < 0:
            raise ValueError("intervalo deve ser >= 0")
        self._fn = fn
        self._intervalo = intervalo
        self._final = final
        self._relogio = relogio
        self._ultimo: float | None = None
        self._guardada: tuple[tuple, dict] | None = None
        self.resultado: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> bool:
        """True se executou agora; False se foi suprimida."""
        agora = self._relogio()
        if self._ultimo is None or agora - self._ultimo >= self._intervalo:
            self._ultimo = agora
            self._guardada = None
            self.resultado = self._fn(*args, **kwargs)
            return True
        if self._final:
            self._guardada = (args, kwargs)
        return False

    def verificar(self) -> bool:
        """Executa a chamada guardada se o intervalo já passou."""
        if self._guardada is None or self._ultimo is None:
            return False
        agora = self._relogio()
        if agora - self._ultimo < self._intervalo:
            return False
        (args, kwargs), self._guardada = self._guardada, None
        self._ultimo = agora
        self.resultado = self._fn(*args, **kwargs)
        return True
