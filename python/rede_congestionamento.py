"""Controle de congestionamento TCP simulado: slow start, AIMD, Tahoe e Reno.

A unidade é o MSS e o tempo avança em RTTs. Eventos de perda são injetados:
'timeout' (RTO) ou 'dupack' (3 ACKs duplicados).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Congestionamento:
    variante: str = "reno"  # "reno" ou "tahoe"
    cwnd: float = 1.0
    ssthresh: float = 64.0
    fase: str = field(default="slow_start", init=False)

    def __post_init__(self) -> None:
        if self.variante not in ("reno", "tahoe"):
            raise ValueError("variante deve ser 'reno' ou 'tahoe'")
        if self.cwnd < 1 or self.ssthresh < 2:
            raise ValueError("cwnd >= 1 e ssthresh >= 2")
        self._atualizar_fase()

    def _atualizar_fase(self) -> None:
        self.fase = "slow_start" if self.cwnd < self.ssthresh else "congestion_avoidance"

    def rtt_sem_perda(self) -> None:
        """Um RTT inteiro com todos os ACKs recebidos."""
        if self.cwnd < self.ssthresh:
            self.cwnd = min(self.cwnd * 2, self.ssthresh)  # crescimento exponencial
        else:
            self.cwnd += 1  # incremento aditivo
        self._atualizar_fase()

    def perda(self, tipo: str) -> None:
        if tipo not in ("timeout", "dupack"):
            raise ValueError("tipo deve ser 'timeout' ou 'dupack'")
        self.ssthresh = max(self.cwnd / 2, 2.0)  # decremento multiplicativo
        if tipo == "dupack" and self.variante == "reno":
            self.cwnd = self.ssthresh  # recuperação rápida
        else:
            self.cwnd = 1.0
        self._atualizar_fase()


def simular(rtts: int, eventos: dict[int, str] | None = None, variante: str = "reno",
            ssthresh: float = 64.0) -> list[float]:
    """cwnd no início de cada RTT; `eventos` mapeia o índice do RTT ao tipo de perda."""
    eventos = eventos or {}
    c = Congestionamento(variante=variante, ssthresh=ssthresh)
    tracado = []
    for r in range(rtts):
        tracado.append(c.cwnd)
        if r in eventos:
            c.perda(eventos[r])
        else:
            c.rtt_sem_perda()
    return tracado


def vazao_media(tracado: list[float], mss: int, rtt_s: float) -> float:
    """Bytes por segundo médios para um traçado de cwnd."""
    if not tracado or rtt_s <= 0:
        raise ValueError("traçado vazio ou RTT inválido")
    return sum(tracado) * mss / (len(tracado) * rtt_s)
