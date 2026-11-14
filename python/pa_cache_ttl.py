"""Decorador de cache com expiração (TTL) e relógio injetável."""
import functools
import time
from typing import Any, Callable, Dict, Tuple


def cache_ttl(segundos: float, relogio: Callable[[], float] = time.monotonic):
    if segundos <= 0:
        raise ValueError("segundos deve ser positivo")

    def decorador(func: Callable) -> Callable:
        armazenado: Dict[Tuple, Tuple[float, Any]] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            chave = (args, tuple(sorted(kwargs.items())))
            agora = relogio()
            if chave in armazenado:
                instante, valor = armazenado[chave]
                if agora - instante < segundos:
                    return valor
            valor = func(*args, **kwargs)
            armazenado[chave] = (agora, valor)
            return valor

        wrapper.limpar = armazenado.clear  # type: ignore[attr-defined]
        return wrapper

    return decorador
