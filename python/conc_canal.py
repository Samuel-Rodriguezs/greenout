"""Canais estilo Go (com ou sem buffer) e `selecionar` sobre vários canais."""
from __future__ import annotations

import threading
from collections import deque
from typing import Any


class CanalFechado(Exception):
    """Operação inválida em canal fechado."""


class Canal:
    """Canal com capacidade `n` (0 = síncrono/sem buffer, como `make(chan T)`)."""

    # um único lock global simplifica o `selecionar` e evita deadlocks entre canais
    _cond = threading.Condition()

    def __init__(self, capacidade: int = 0) -> None:
        if capacidade < 0:
            raise ValueError("capacidade deve ser >= 0")
        self.capacidade = capacidade
        self._buffer: deque[Any] = deque()
        self._fechado = False
        self._receptores = 0  # receptores bloqueados (permite enviar em canal síncrono)

    # -- predicados (chamados com _cond travado) -------------------------------
    def _pode_enviar(self) -> bool:
        if self._fechado:
            return True  # vai levantar erro
        if self.capacidade == 0:
            return len(self._buffer) < self._receptores
        return len(self._buffer) < self.capacidade

    def _pode_receber(self) -> bool:
        return bool(self._buffer) or self._fechado

    def _enviar(self, valor: Any) -> None:
        if self._fechado:
            raise CanalFechado("envio em canal fechado")
        self._buffer.append(valor)
        Canal._cond.notify_all()

    def _receber(self) -> tuple[Any, bool]:
        if self._buffer:
            v = self._buffer.popleft()
            Canal._cond.notify_all()
            return v, True
        return None, False  # fechado e vazio

    # -- API pública -------------------------------------------------------------
    def enviar(self, valor: Any, timeout: float | None = None) -> None:
        with Canal._cond:
            if not Canal._cond.wait_for(self._pode_enviar, timeout):
                raise TimeoutError("envio bloqueado")
            self._enviar(valor)

    def receber(self, timeout: float | None = None) -> tuple[Any, bool]:
        """Retorna (valor, ok); ok=False quando o canal está fechado e vazio."""
        with Canal._cond:
            self._receptores += 1
            Canal._cond.notify_all()
            try:
                if not Canal._cond.wait_for(self._pode_receber, timeout):
                    raise TimeoutError("recepção bloqueada")
                return self._receber()
            finally:
                self._receptores -= 1

    def fechar(self) -> None:
        with Canal._cond:
            if self._fechado:
                raise CanalFechado("canal já fechado")
            self._fechado = True
            Canal._cond.notify_all()

    def __iter__(self):
        while True:
            v, ok = self.receber()
            if not ok:
                return
            yield v



def selecionar(
    casos: list[tuple[str, Canal] | tuple[str, Canal, Any]],
    padrao: bool = False,
    timeout: float | None = None,
) -> tuple[int, Any, bool]:
    """Como o `select` do Go. Cada caso é ("recv", canal) ou ("send", canal, valor).

    Retorna (índice do caso, valor recebido, ok). Com `padrao=True` retorna
    (-1, None, False) se nenhum caso estiver pronto. Entre casos prontos, o de
    menor índice vence (determinístico).
    """
    with Canal._cond:
        recebendo = [c for tipo, c, *_ in casos if tipo == "recv"]
        for c in recebendo:
            c._receptores += 1
        Canal._cond.notify_all()

        def pronto() -> int:
            for i, caso in enumerate(casos):
                tipo, canal = caso[0], caso[1]
                if tipo == "recv" and canal._pode_receber():
                    return i
                if tipo == "send" and canal._pode_enviar():
                    return i
            return -1

        try:
            if padrao:
                i = pronto()
                if i < 0:
                    return -1, None, False
            else:
                achou: list[int] = []

                def pred() -> bool:
                    achou[:] = [pronto()]
                    return achou[0] >= 0

                if not Canal._cond.wait_for(pred, timeout):
                    raise TimeoutError("nenhum caso pronto")
                i = achou[0]
            caso = casos[i]
            if caso[0] == "recv":
                v, ok = caso[1]._receber()
                return i, v, ok
            caso[1]._enviar(caso[2])
            return i, None, True
        finally:
            for c in recebendo:
                c._receptores -= 1
