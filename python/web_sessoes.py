"""Sessões em memória com expiração (deslizante ou absoluta) e relógio injetável."""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Sessao:
    id: str
    dados: dict[str, Any] = field(default_factory=dict)
    criada_em: float = 0.0
    ultimo_acesso: float = 0.0


class ArmazemSessoes:
    def __init__(self, ttl: float = 1800.0, relogio: Callable[[], float] | None = None,
                 gerar_id: Callable[[], str] | None = None, deslizante: bool = True,
                 duracao_maxima: float | None = None) -> None:
        if ttl <= 0:
            raise ValueError("ttl deve ser positivo")
        import time
        self.ttl = ttl
        self.relogio = relogio or time.monotonic
        self.gerar_id = gerar_id or (lambda: secrets.token_urlsafe(24))
        self.deslizante = deslizante
        self.duracao_maxima = duracao_maxima
        self._sessoes: dict[str, Sessao] = {}

    def _expirada(self, s: Sessao) -> bool:
        agora = self.relogio()
        if agora - s.ultimo_acesso >= self.ttl:
            return True
        return self.duracao_maxima is not None and agora - s.criada_em >= self.duracao_maxima

    def criar(self, dados: dict[str, Any] | None = None) -> Sessao:
        agora = self.relogio()
        sid = self.gerar_id()
        while sid in self._sessoes:
            sid = self.gerar_id()
        s = Sessao(sid, dict(dados or {}), agora, agora)
        self._sessoes[sid] = s
        return s

    def obter(self, sid: str | None) -> Sessao | None:
        if not sid:
            return None
        s = self._sessoes.get(sid)
        if s is None:
            return None
        if self._expirada(s):
            del self._sessoes[sid]
            return None
        if self.deslizante:
            s.ultimo_acesso = self.relogio()
        return s

    def destruir(self, sid: str) -> bool:
        return self._sessoes.pop(sid, None) is not None

    def regenerar(self, sid: str) -> Sessao | None:
        """Troca o id mantendo os dados (previne fixação de sessão)."""
        antiga = self.obter(sid)
        if antiga is None:
            return None
        self.destruir(sid)
        return self.criar(antiga.dados)

    def limpar_expiradas(self) -> int:
        mortas = [k for k, s in self._sessoes.items() if self._expirada(s)]
        for k in mortas:
            del self._sessoes[k]
        return len(mortas)

    def __len__(self) -> int:
        return len(self._sessoes)
