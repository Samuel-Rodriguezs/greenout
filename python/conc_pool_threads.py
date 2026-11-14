"""Pool de threads próprio com futuros simples."""
from __future__ import annotations

import queue
import threading
from typing import Any, Callable


class TarefaFuturo:
    """Resultado de uma tarefa submetida ao pool."""

    def __init__(self) -> None:
        self._pronto = threading.Event()
        self._resultado: Any = None
        self._erro: BaseException | None = None

    def _definir(self, resultado: Any, erro: BaseException | None) -> None:
        self._resultado = resultado
        self._erro = erro
        self._pronto.set()

    def pronto(self) -> bool:
        return self._pronto.is_set()

    def resultado(self, timeout: float | None = None) -> Any:
        if not self._pronto.wait(timeout):
            raise TimeoutError("tarefa não concluída")
        if self._erro is not None:
            raise self._erro
        return self._resultado


_PARAR = object()


class PoolThreads:
    """Pool com N workers que consomem uma fila de tarefas."""

    def __init__(self, n_workers: int) -> None:
        if n_workers < 1:
            raise ValueError("n_workers deve ser >= 1")
        self._fila: queue.Queue = queue.Queue()
        self._fechado = False
        self._lock = threading.Lock()
        self._threads = [
            threading.Thread(target=self._trabalhar, daemon=True)
            for _ in range(n_workers)
        ]
        for t in self._threads:
            t.start()

    def _trabalhar(self) -> None:
        while True:
            item = self._fila.get()
            if item is _PARAR:
                return
            fn, args, futuro = item
            try:
                futuro._definir(fn(*args), None)
            except BaseException as exc:  # noqa: BLE001
                futuro._definir(None, exc)

    def submeter(self, fn: Callable[..., Any], *args: Any) -> TarefaFuturo:
        with self._lock:
            if self._fechado:
                raise RuntimeError("pool encerrado")
            futuro = TarefaFuturo()
            self._fila.put((fn, args, futuro))
            return futuro

    def mapear(self, fn: Callable[[Any], Any], itens: list[Any]) -> list[Any]:
        futuros = [self.submeter(fn, i) for i in itens]
        return [f.resultado(5) for f in futuros]

    def encerrar(self) -> None:
        with self._lock:
            if self._fechado:
                return
            self._fechado = True
            for _ in self._threads:
                self._fila.put(_PARAR)
        for t in self._threads:
            t.join(5)

    def __enter__(self) -> "PoolThreads":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.encerrar()
