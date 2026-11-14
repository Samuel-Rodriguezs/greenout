"""Máquina de estados TCP (RFC 793): handshake de 3 vias e encerramento."""
from __future__ import annotations

from enum import Enum


class Estado(Enum):
    CLOSED = "CLOSED"
    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RCVD = "SYN_RCVD"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT_1 = "FIN_WAIT_1"
    FIN_WAIT_2 = "FIN_WAIT_2"
    CLOSING = "CLOSING"
    TIME_WAIT = "TIME_WAIT"
    CLOSE_WAIT = "CLOSE_WAIT"
    LAST_ACK = "LAST_ACK"


# Eventos do usuário
ABRIR_ATIVO, ABRIR_PASSIVO, FECHAR = "abrir_ativo", "abrir_passivo", "fechar"
# Eventos de segmentos recebidos
RCV_SYN, RCV_SYN_ACK, RCV_ACK, RCV_FIN, RCV_FIN_ACK, RCV_RST = (
    "rcv_syn", "rcv_syn_ack", "rcv_ack", "rcv_fin", "rcv_fin_ack", "rcv_rst",
)
# Temporizador
TIMEOUT_2MSL = "timeout_2msl"

# (estado, evento) -> (novo estado, segmento enviado ou None)
_TRANSICOES: dict[tuple[Estado, str], tuple[Estado, str | None]] = {
    (Estado.CLOSED, ABRIR_PASSIVO): (Estado.LISTEN, None),
    (Estado.CLOSED, ABRIR_ATIVO): (Estado.SYN_SENT, "SYN"),
    (Estado.LISTEN, RCV_SYN): (Estado.SYN_RCVD, "SYN+ACK"),
    (Estado.LISTEN, ABRIR_ATIVO): (Estado.SYN_SENT, "SYN"),
    (Estado.LISTEN, FECHAR): (Estado.CLOSED, None),
    (Estado.SYN_SENT, RCV_SYN_ACK): (Estado.ESTABLISHED, "ACK"),
    (Estado.SYN_SENT, RCV_SYN): (Estado.SYN_RCVD, "SYN+ACK"),  # abertura simultânea
    (Estado.SYN_SENT, FECHAR): (Estado.CLOSED, None),
    (Estado.SYN_RCVD, RCV_ACK): (Estado.ESTABLISHED, None),
    (Estado.SYN_RCVD, FECHAR): (Estado.FIN_WAIT_1, "FIN"),
    (Estado.ESTABLISHED, FECHAR): (Estado.FIN_WAIT_1, "FIN"),
    (Estado.ESTABLISHED, RCV_FIN): (Estado.CLOSE_WAIT, "ACK"),
    (Estado.FIN_WAIT_1, RCV_ACK): (Estado.FIN_WAIT_2, None),
    (Estado.FIN_WAIT_1, RCV_FIN): (Estado.CLOSING, "ACK"),
    (Estado.FIN_WAIT_1, RCV_FIN_ACK): (Estado.TIME_WAIT, "ACK"),
    (Estado.FIN_WAIT_2, RCV_FIN): (Estado.TIME_WAIT, "ACK"),
    (Estado.CLOSING, RCV_ACK): (Estado.TIME_WAIT, None),
    (Estado.TIME_WAIT, TIMEOUT_2MSL): (Estado.CLOSED, None),
    (Estado.CLOSE_WAIT, FECHAR): (Estado.LAST_ACK, "FIN"),
    (Estado.LAST_ACK, RCV_ACK): (Estado.CLOSED, None),
}

# RST aborta qualquer estado sincronizado; em LISTEN é ignorado
_RST_ABORTA = {
    Estado.SYN_SENT, Estado.SYN_RCVD, Estado.ESTABLISHED, Estado.FIN_WAIT_1,
    Estado.FIN_WAIT_2, Estado.CLOSING, Estado.TIME_WAIT, Estado.CLOSE_WAIT,
    Estado.LAST_ACK,
}


class TransicaoInvalida(Exception):
    pass


class ConexaoTCP:
    def __init__(self) -> None:
        self.estado = Estado.CLOSED
        self.historico: list[Estado] = [Estado.CLOSED]

    def processar(self, evento: str) -> str | None:
        """Aplica o evento; devolve o segmento a enviar ('SYN', 'ACK', ...)."""
        if evento == RCV_RST:
            if self.estado in _RST_ABORTA:
                self._ir(Estado.CLOSED)
                return None
            if self.estado == Estado.LISTEN:
                return None
        chave = (self.estado, evento)
        if chave not in _TRANSICOES:
            raise TransicaoInvalida(f"{evento!r} inválido em {self.estado.value}")
        novo, saida = _TRANSICOES[chave]
        self._ir(novo)
        return saida

    def _ir(self, novo: Estado) -> None:
        self.estado = novo
        self.historico.append(novo)

    @property
    def sincronizada(self) -> bool:
        return self.estado == Estado.ESTABLISHED
