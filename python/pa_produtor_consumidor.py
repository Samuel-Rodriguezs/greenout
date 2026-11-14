"""Produtor/consumidor com threading e queue.Queue limitada."""
import queue
import threading
from typing import Callable, Iterable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")
_FIM = object()


def processar_em_paralelo(
    itens: Iterable[T], funcao: Callable[[T], R], consumidores: int = 3, capacidade: int = 4
) -> List[R]:
    """Processa itens com N threads consumidoras; devolve resultados na ordem de entrada.

    Se funcao levantar, a primeira exceção é re-lançada após o encerramento limpo.
    """
    if consumidores < 1 or capacidade < 1:
        raise ValueError("consumidores e capacidade devem ser >= 1")
    fila: "queue.Queue" = queue.Queue(maxsize=capacidade)
    resultados: dict = {}
    erros: List[BaseException] = []
    trava = threading.Lock()

    def consumir() -> None:
        while True:
            tarefa = fila.get()
            if tarefa is _FIM:
                return
            idx, item = tarefa
            try:
                valor = funcao(item)
                with trava:
                    resultados[idx] = valor
            except Exception as e:  # noqa: BLE001
                with trava:
                    erros.append(e)

    threads = [threading.Thread(target=consumir, daemon=True) for _ in range(consumidores)]
    for t in threads:
        t.start()
    total = 0
    for idx, item in enumerate(itens):
        fila.put((idx, item))
        total += 1
    for _ in threads:
        fila.put(_FIM)
    for t in threads:
        t.join()
    if erros:
        raise erros[0]
    return [resultados[i] for i in range(total)]
