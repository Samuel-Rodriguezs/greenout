"""Decorador de repetição com backoff exponencial."""
import functools
import time
from typing import Callable, Tuple, Type


def retry(
    tentativas: int = 3,
    atraso: float = 0.1,
    fator: float = 2.0,
    excecoes: Tuple[Type[BaseException], ...] = (Exception,),
    dormir: Callable[[float], None] = time.sleep,
):
    if tentativas < 1:
        raise ValueError("tentativas deve ser >= 1")

    def decorador(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            espera = atraso
            for n in range(1, tentativas + 1):
                try:
                    return func(*args, **kwargs)
                except excecoes:
                    if n == tentativas:
                        raise
                    dormir(espera)
                    espera *= fator

        return wrapper

    return decorador
