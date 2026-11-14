"""Retry assíncrono com backoff exponencial, jitter e sleep injetáveis."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable


class TentativasEsgotadas(Exception):
    def __init__(self, tentativas: int, ultimo: BaseException) -> None:
        super().__init__(f"falhou após {tentativas} tentativas: {ultimo!r}")
        self.tentativas = tentativas
        self.ultimo = ultimo


def atraso_backoff(
    tentativa: int,
    base: float = 0.1,
    fator: float = 2.0,
    maximo: float = 10.0,
    jitter: Callable[[float], float] | None = None,
) -> float:
    """Atraso antes da tentativa seguinte (tentativa começa em 1)."""
    atraso = min(maximo, base * fator ** (tentativa - 1))
    return jitter(atraso) if jitter else atraso


async def com_retry(
    fn: Callable[[], Awaitable[Any]],
    tentativas: int = 3,
    base: float = 0.1,
    fator: float = 2.0,
    maximo: float = 10.0,
    excecoes: tuple[type[BaseException], ...] = (Exception,),
    dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    jitter: Callable[[float], float] | None = None,
) -> Any:
    if tentativas < 1:
        raise ValueError("tentativas deve ser >= 1")
    ultimo: BaseException | None = None
    for n in range(1, tentativas + 1):
        try:
            return await fn()
        except excecoes as exc:
            ultimo = exc
            if n < tentativas:
                await dormir(atraso_backoff(n, base, fator, maximo, jitter))
    assert ultimo is not None
    raise TentativasEsgotadas(tentativas, ultimo)
