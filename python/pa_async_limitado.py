"""asyncio: execução concorrente com limite (semáforo) e timeout por tarefa."""
import asyncio
from typing import Awaitable, Callable, Iterable, List, Optional, TypeVar, Union

T = TypeVar("T")
R = TypeVar("R")


async def executar_limitado(
    itens: Iterable[T],
    corrotina: Callable[[T], Awaitable[R]],
    limite: int = 3,
    timeout: Optional[float] = None,
) -> List[Union[R, BaseException]]:
    """Roda corrotina(item) para todos, no máximo `limite` simultâneos.

    Mantém a ordem; falhas e timeouts voltam como exceção no resultado (não abortam as demais).
    """
    if limite < 1:
        raise ValueError("limite deve ser >= 1")
    semaforo = asyncio.Semaphore(limite)

    async def uma(item: T) -> R:
        async with semaforo:
            return await asyncio.wait_for(corrotina(item), timeout)

    return await asyncio.gather(*(uma(i) for i in itens), return_exceptions=True)
