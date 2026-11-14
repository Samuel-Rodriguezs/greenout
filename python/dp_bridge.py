"""Bridge: notificações (abstração) separadas dos canais de envio (implementação)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Canal(ABC):
    @abstractmethod
    def enviar(self, destino: str, texto: str) -> None: ...


class CanalEmail(Canal):
    def __init__(self) -> None:
        self.caixa: list[tuple[str, str]] = []

    def enviar(self, destino: str, texto: str) -> None:
        self.caixa.append((destino, f"Assunto: aviso\n{texto}"))


class CanalSms(Canal):
    def __init__(self) -> None:
        self.caixa: list[tuple[str, str]] = []

    def enviar(self, destino: str, texto: str) -> None:
        self.caixa.append((destino, texto[:40]))


class Notificacao(ABC):
    def __init__(self, canal: Canal) -> None:
        self.canal = canal

    @abstractmethod
    def notificar(self, destino: str, dado: str) -> None: ...


class AvisoCobranca(Notificacao):
    def notificar(self, destino: str, dado: str) -> None:
        self.canal.enviar(destino, f"Cobranca pendente: {dado}")


class AvisoEntrega(Notificacao):
    def notificar(self, destino: str, dado: str) -> None:
        self.canal.enviar(destino, f"Pedido {dado} saiu para entrega")
