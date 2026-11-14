"""Modelo de atores simples: mailbox + thread processando mensagens em ordem."""
from __future__ import annotations

import queue
import threading
from typing import Any, Callable

_PARAR = object()


class Ator:
    """Ator com estado privado; `receber(estado, msg)` devolve o novo estado."""

    def __init__(self, receber: Callable[[Any, Any], Any], estado: Any = None) -> None:
        self._receber = receber
        self._estado = estado
        self._caixa: queue.Queue = queue.Queue()
        self.erros: list[BaseException] = []
        self._thread = threading.Thread(target=self._laco, daemon=True)
        self._ativo = True
        self._thread.start()

    def _laco(self) -> None:
        while True:
            msg = self._caixa.get()
            if msg is _PARAR:
                return
            try:
                self._estado = self._receber(self._estado, msg)
            except BaseException as exc:  # noqa: BLE001
                self.erros.append(exc)

    def enviar(self, msg: Any) -> None:
        if not self._ativo:
            raise RuntimeError("ator parado")
        self._caixa.put(msg)

    def perguntar(self, msg: Any, timeout: float = 2.0) -> Any:
        """Envia (msg, resposta_queue) e aguarda resposta; ator deve responder a ela."""
        resp: queue.Queue = queue.Queue(maxsize=1)
        self.enviar(("pergunta", msg, resp))
        return resp.get(timeout=timeout)

    def parar(self, timeout: float = 2.0) -> Any:
        """Processa as mensagens pendentes, encerra e devolve o estado final."""
        if self._ativo:
            self._ativo = False
            self._caixa.put(_PARAR)
        self._thread.join(timeout)
        return self._estado


def contador() -> Ator:
    """Exemplo: ator contador que responde a 'inc', 'dec' e perguntas 'valor'."""

    def receber(estado: int, msg: Any) -> int:
        if isinstance(msg, tuple) and msg[0] == "pergunta":
            msg[2].put(estado)
            return estado
        if msg == "inc":
            return estado + 1
        if msg == "dec":
            return estado - 1
        raise ValueError(f"mensagem desconhecida: {msg!r}")

    return Ator(receber, 0)
