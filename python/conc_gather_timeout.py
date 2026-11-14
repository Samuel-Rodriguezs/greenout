"""Gather com timeout global e cancelamento limpo das tarefas pendentes."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Iterable


@dataclass
class ResultadoGather:
    resultados: list[Any]  # valor, exceção ou None se cancelada
    concluidas: list[int] = field(default_factory=list)
    falhas: list[int] = field(default_factory=list)
    canceladas: list[int] = field(default_factory=list)

    @property
    def completo(self) -> bool:
        return not self.canceladas


async def gather_com_timeout(
    aws: Iterable[Awaitable[Any]],
    timeout: float,
    falhar_rapido: bool = False,
) -> ResultadoGather:
    """Aguarda todas as awaitables até `timeout`; as que sobrarem são canceladas.

    Com `falhar_rapido`, a primeira exceção também cancela as restantes.
    """
    tarefas = [asyncio.ensure_future(a) for a in aws]
    if not tarefas:
        return ResultadoGather([])
    modo = asyncio.FIRST_EXCEPTION if falhar_rapido else asyncio.ALL_COMPLETED
    _, pendentes = await asyncio.wait(tarefas, timeout=timeout, return_when=modo)
    for t in pendentes:
        t.cancel()
    if pendentes:
        await asyncio.gather(*pendentes, return_exceptions=True)  # aguarda o cancelamento

    res = ResultadoGather([None] * len(tarefas))
    for i, t in enumerate(tarefas):
        if t.cancelled():
            res.canceladas.append(i)
        elif t.exception() is not None:
            res.resultados[i] = t.exception()
            res.falhas.append(i)
        else:
            res.resultados[i] = t.result()
            res.concluidas.append(i)
    return res
