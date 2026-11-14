"""Lock distribuído simulado com lease (expiração) e fencing token."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Concessao:
    recurso: str
    dono: str
    token: int  # fencing token monotônico
    expira_em: float


class ServidorLocks:
    """Serviço central de locks; o relógio é injetável para testes."""

    def __init__(self, relogio: Callable[[], float] = time.monotonic) -> None:
        self._relogio = relogio
        self._lock = threading.Lock()
        self._atuais: dict[str, Concessao] = {}
        self._contador = 0

    def _vigente(self, recurso: str) -> Concessao | None:
        c = self._atuais.get(recurso)
        if c is not None and c.expira_em <= self._relogio():
            del self._atuais[recurso]
            return None
        return c

    def adquirir(self, recurso: str, dono: str, lease: float) -> Concessao | None:
        if lease <= 0:
            raise ValueError("lease deve ser > 0")
        with self._lock:
            atual = self._vigente(recurso)
            if atual is not None and atual.dono != dono:
                return None
            if atual is not None:  # reentrada do mesmo dono: renova mantendo o token
                nova = Concessao(recurso, dono, atual.token, self._relogio() + lease)
            else:
                self._contador += 1
                nova = Concessao(recurso, dono, self._contador, self._relogio() + lease)
            self._atuais[recurso] = nova
            return nova

    def renovar(self, concessao: Concessao, lease: float) -> Concessao | None:
        """Renova se a concessão ainda for a vigente; senão devolve None."""
        with self._lock:
            atual = self._vigente(concessao.recurso)
            if atual is None or atual.token != concessao.token or atual.dono != concessao.dono:
                return None
            nova = Concessao(atual.recurso, atual.dono, atual.token, self._relogio() + lease)
            self._atuais[atual.recurso] = nova
            return nova

    def liberar(self, concessao: Concessao) -> bool:
        with self._lock:
            atual = self._vigente(concessao.recurso)
            if atual is None or atual.token != concessao.token:
                return False
            del self._atuais[concessao.recurso]
            return True

    def dono_de(self, recurso: str) -> str | None:
        with self._lock:
            c = self._vigente(recurso)
            return c.dono if c else None


class RecursoProtegido:
    """Recurso que rejeita escritas com fencing token antigo."""

    def __init__(self) -> None:
        self.maior_token = 0
        self.valor: object = None

    def escrever(self, token: int, valor: object) -> bool:
        if token < self.maior_token:
            return False
        self.maior_token = token
        self.valor = valor
        return True
