"""Cronômetro que funciona como context manager e como decorador."""
import functools
import time
from typing import Callable, Optional


class Cronometro:
    def __init__(self, relogio: Callable[[], float] = time.perf_counter) -> None:
        self._relogio = relogio
        self._inicio: Optional[float] = None
        self.decorrido: Optional[float] = None

    def __enter__(self) -> "Cronometro":
        self._inicio = self._relogio()
        self.decorrido = None
        return self

    def __exit__(self, tipo, valor, tb) -> bool:
        self.decorrido = self._relogio() - self._inicio
        return False  # nunca suprime exceções

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper
