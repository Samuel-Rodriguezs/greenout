"""Round Robin com quantum.

Convenção clássica: se um processo chega no mesmo instante em que outro
esgota o quantum, o recém-chegado entra na fila antes do preemptado.
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from so_sched_basico import Processo, Resultado, metricas, validar


def round_robin(procs: list[Processo], quantum: int) -> Resultado:
    if quantum <= 0:
        raise ValueError("quantum deve ser positivo")
    validar(procs)
    chegadas = sorted(procs, key=lambda p: p.chegada)  # sort estável
    restante = {p.pid: p.surto for p in procs}
    fila: deque[Processo] = deque()
    linha: list[Optional[str]] = []
    prox = 0
    t = 0

    def admitir() -> None:
        nonlocal prox
        while prox < len(chegadas) and chegadas[prox].chegada <= t:
            fila.append(chegadas[prox])
            prox += 1

    admitir()
    while fila or prox < len(chegadas):
        if not fila:
            linha.append(None)
            t += 1
            admitir()
            continue
        p = fila.popleft()
        fatia = min(quantum, restante[p.pid])
        linha.extend([p.pid] * fatia)
        restante[p.pid] -= fatia
        t += fatia
        admitir()
        if restante[p.pid] > 0:
            fila.append(p)
    return metricas(procs, tuple(linha))


def trocas_de_contexto(resultado: Resultado) -> int:
    """Número de trocas entre processos distintos (ocioso não conta como troca)."""
    execs = [pid for pid, _, _ in resultado.segmentos() if pid is not None]
    return sum(1 for a, b in zip(execs, execs[1:]) if a != b)
