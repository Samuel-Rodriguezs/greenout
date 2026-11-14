"""Escalonamento por prioridade (número menor = prioridade maior) com aging.

Aging: a cada `intervalo` unidades consecutivas esperando na fila de prontos,
a prioridade efetiva de um processo melhora em `passo` (nunca abaixo de 0).
Isso evita a inanição (starvation) de processos de baixa prioridade.
"""
from __future__ import annotations

from typing import Optional

from so_sched_basico import Processo, Resultado, metricas, validar


def prioridade(
    procs: list[Processo],
    preemptivo: bool = True,
    intervalo: Optional[int] = None,
    passo: int = 1,
) -> Resultado:
    """Simula prioridade; `intervalo=None` desliga o aging."""
    validar(procs)
    if intervalo is not None and (intervalo <= 0 or passo <= 0):
        raise ValueError("intervalo e passo devem ser positivos")
    restante = {p.pid: p.surto for p in procs}
    efetiva = {p.pid: p.prioridade for p in procs}
    espera = {p.pid: 0 for p in procs}
    ordem = {p.pid: i for i, p in enumerate(procs)}
    linha: list[Optional[str]] = []
    atual: Optional[Processo] = None
    t = 0
    while any(r > 0 for r in restante.values()):
        prontos = [p for p in procs if p.chegada <= t and restante[p.pid] > 0]
        if not prontos:
            linha.append(None)
            atual = None
            t += 1
            continue
        if preemptivo or atual is None or restante[atual.pid] == 0:
            atual = min(prontos, key=lambda p: (efetiva[p.pid], p.chegada, ordem[p.pid]))
        linha.append(atual.pid)
        restante[atual.pid] -= 1
        espera[atual.pid] = 0
        if intervalo is not None:
            for p in prontos:
                if p is atual:
                    continue
                espera[p.pid] += 1
                if espera[p.pid] == intervalo:
                    efetiva[p.pid] = max(0, efetiva[p.pid] - passo)
                    espera[p.pid] = 0
        t += 1
    return metricas(procs, tuple(linha))
