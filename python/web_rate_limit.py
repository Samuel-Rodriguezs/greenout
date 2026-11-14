"""Rate limiter por janela deslizante (log de timestamps) com relógio injetável."""
from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable

from web_http import Requisicao, Resposta
from web_middleware import Manipulador, Middleware


@dataclass(frozen=True)
class Decisao:
    permitido: bool
    restantes: int
    retry_apos: float  # segundos até liberar (0 se permitido)


class LimitadorJanela:
    def __init__(self, limite: int, janela: float, relogio: Callable[[], float] | None = None) -> None:
        if limite < 1 or janela <= 0:
            raise ValueError("limite >= 1 e janela > 0")
        self.limite = limite
        self.janela = janela
        self.relogio = relogio or time.monotonic
        self._eventos: dict[str, deque[float]] = {}

    def _podar(self, fila: deque[float], agora: float) -> None:
        while fila and agora - fila[0] >= self.janela:
            fila.popleft()

    def verificar(self, chave: str) -> Decisao:
        """Consome uma unidade se houver cota; nega sem consumir caso contrário."""
        agora = self.relogio()
        fila = self._eventos.setdefault(chave, deque())
        self._podar(fila, agora)
        if len(fila) >= self.limite:
            return Decisao(False, 0, fila[0] + self.janela - agora)
        fila.append(agora)
        return Decisao(True, self.limite - len(fila), 0.0)

    def limpar(self) -> int:
        """Remove chaves sem eventos na janela; devolve quantas foram removidas."""
        agora = self.relogio()
        vazias = []
        for k, fila in self._eventos.items():
            self._podar(fila, agora)
            if not fila:
                vazias.append(k)
        for k in vazias:
            del self._eventos[k]
        return len(vazias)


def mw_rate_limit(limitador: LimitadorJanela,
                  chave: Callable[[Requisicao], str] = lambda r: r.cabecalhos.get("X-Forwarded-For", "anon") or "anon"
                  ) -> Middleware:
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        d = limitador.verificar(chave(req))
        if not d.permitido:
            resp = Resposta.de_texto("Muitas requisições", 429)
            resp.cabecalhos["Retry-After"] = str(math.ceil(d.retry_apos))
        else:
            resp = proximo(req)
        resp.cabecalhos["X-RateLimit-Limit"] = str(limitador.limite)
        resp.cabecalhos["X-RateLimit-Remaining"] = str(d.restantes)
        return resp
    return mw
