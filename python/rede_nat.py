"""NAT/PAT com tabela de traduções, timeouts e pool de portas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

Endpoint = tuple[int, int]  # (ip, porta)


@dataclass
class Traducao:
    interno: Endpoint
    externo: Endpoint  # (ip público, porta pública)
    protocolo: str
    ultimo_uso: float


class NAT:
    def __init__(self, ip_publico: int, faixa_portas: tuple[int, int] = (49152, 65535),
                 timeout: float = 60.0, relogio: Callable[[], float] | None = None) -> None:
        ini, fim = faixa_portas
        if not 0 < ini <= fim <= 65535:
            raise ValueError("faixa de portas inválida")
        self.ip_publico = ip_publico
        self._ini, self._fim = ini, fim
        self.timeout = timeout
        self._relogio = relogio or (lambda: 0.0)
        self._saida: dict[tuple[str, Endpoint], Traducao] = {}
        self._entrada: dict[tuple[str, int], Traducao] = {}
        self._proxima = ini

    def _alocar_porta(self, proto: str) -> int:
        total = self._fim - self._ini + 1
        for _ in range(total):
            p = self._proxima
            self._proxima = self._ini if p >= self._fim else p + 1
            if (proto, p) not in self._entrada:
                return p
        raise RuntimeError("pool de portas esgotado")

    def traduzir_saida(self, proto: str, interno: Endpoint) -> Endpoint:
        """Pacote LAN -> internet: devolve o endpoint público (cria a entrada se preciso)."""
        agora = self._relogio()
        t = self._saida.get((proto, interno))
        if t is None:
            self.expirar()
            porta = self._alocar_porta(proto)
            t = Traducao(interno, (self.ip_publico, porta), proto, agora)
            self._saida[(proto, interno)] = t
            self._entrada[(proto, porta)] = t
        t.ultimo_uso = agora
        return t.externo

    def traduzir_entrada(self, proto: str, porta_publica: int) -> Endpoint | None:
        """Resposta internet -> LAN; None se não houver tradução (descartar)."""
        t = self._entrada.get((proto, porta_publica))
        if t is None:
            return None
        agora = self._relogio()
        if agora - t.ultimo_uso >= self.timeout:
            self._remover(t)
            return None
        t.ultimo_uso = agora
        return t.interno

    def _remover(self, t: Traducao) -> None:
        self._saida.pop((t.protocolo, t.interno), None)
        self._entrada.pop((t.protocolo, t.externo[1]), None)

    def expirar(self) -> int:
        agora = self._relogio()
        vencidas = [t for t in self._saida.values() if agora - t.ultimo_uso >= self.timeout]
        for t in vencidas:
            self._remover(t)
        return len(vencidas)

    def adicionar_redirecionamento(self, proto: str, porta_publica: int, interno: Endpoint) -> None:
        """Port forwarding estático (nunca expira)."""
        if (proto, porta_publica) in self._entrada:
            raise ValueError("porta pública já em uso")
        t = Traducao(interno, (self.ip_publico, porta_publica), proto, float("inf"))
        self._saida[(proto, interno)] = t
        self._entrada[(proto, porta_publica)] = t

    def __len__(self) -> int:
        return len(self._saida)
