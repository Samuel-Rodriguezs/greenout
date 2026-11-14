"""Pipeline de estágios, cada um em sua thread, ligados por filas limitadas."""
from __future__ import annotations

import queue
import threading
from typing import Any, Callable, Iterable

_FIM = object()


class PipelineThreads:
    """Cada estágio é uma função item -> item. Retornar `DESCARTAR` filtra o item."""

    DESCARTAR = object()

    def __init__(self, estagios: list[Callable[[Any], Any]], capacidade: int = 4) -> None:
        if not estagios:
            raise ValueError("é preciso ao menos um estágio")
        self.estagios = estagios
        self.capacidade = capacidade

    def executar(self, entrada: Iterable[Any], timeout: float = 5.0) -> list[Any]:
        n = len(self.estagios)
        filas: list[queue.Queue] = [queue.Queue(self.capacidade) for _ in range(n + 1)]
        erros: list[BaseException] = []

        def estagio(i: int) -> None:
            fn, ent, sai = self.estagios[i], filas[i], filas[i + 1]
            while True:
                item = ent.get()
                if item is _FIM:
                    sai.put(_FIM)
                    return
                if erros:
                    continue  # drena a entrada após erro
                try:
                    r = fn(item)
                except BaseException as exc:  # noqa: BLE001
                    erros.append(exc)
                    continue
                if r is not self.DESCARTAR:
                    sai.put(r)

        threads = [threading.Thread(target=estagio, args=(i,), daemon=True) for i in range(n)]
        for t in threads:
            t.start()

        saida: list[Any] = []

        def coletar() -> None:
            while True:
                item = filas[-1].get()
                if item is _FIM:
                    return
                saida.append(item)

        coletor = threading.Thread(target=coletar, daemon=True)
        coletor.start()

        for item in entrada:
            filas[0].put(item)
        filas[0].put(_FIM)

        for t in threads:
            t.join(timeout)
        coletor.join(timeout)
        if erros:
            raise erros[0]
        return saida
