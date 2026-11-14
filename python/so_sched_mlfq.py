"""Fila multinível com realimentação (MLFQ).

Regras:
1. Todo processo novo entra no nível 0 (maior prioridade).
2. Executa-se sempre o primeiro processo do nível mais alto não vazio.
3. Processo que consome o quantum do nível desce um nível (no último nível
   continua girando em Round Robin).
4. Processo de nível mais baixo é preemptado quando chega alguém acima; ele
   volta ao fim da fila do seu nível com o quantum zerado.
5. Opcionalmente, a cada `reforco` unidades todos sobem para o nível 0
   (priority boost), evitando inanição.
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from so_sched_basico import Processo, Resultado, metricas, validar


def mlfq(
    procs: list[Processo],
    quanta: tuple[int, ...] = (2, 4, 8),
    reforco: Optional[int] = None,
) -> tuple[Resultado, tuple[Optional[int], ...]]:
    """Retorna o resultado e o nível em que rodou a cada unidade (None = ocioso)."""
    validar(procs)
    if not quanta or any(q <= 0 for q in quanta):
        raise ValueError("quanta inválidos")
    if reforco is not None and reforco <= 0:
        raise ValueError("reforco deve ser positivo")
    ultimo = len(quanta) - 1
    filas: list[deque[Processo]] = [deque() for _ in quanta]
    restante = {p.pid: p.surto for p in procs}
    chegando = sorted(procs, key=lambda p: p.chegada)
    prox = 0
    atual: Optional[Processo] = None
    nivel = 0
    usado = 0
    linha: list[Optional[str]] = []
    niveis: list[Optional[int]] = []
    t = 0
    while atual is not None or prox < len(chegando) or any(filas):
        if reforco is not None and t > 0 and t % reforco == 0:
            todos = [p for f in filas for p in f]
            if atual is not None:
                todos.insert(0, atual)
                atual = None
            for f in filas:
                f.clear()
            filas[0].extend(todos)
        while prox < len(chegando) and chegando[prox].chegada <= t:
            filas[0].append(chegando[prox])
            prox += 1
        if atual is not None and any(filas[n] for n in range(nivel)):
            filas[nivel].append(atual)
            atual = None
        if atual is None:
            for n, f in enumerate(filas):
                if f:
                    atual, nivel, usado = f.popleft(), n, 0
                    break
        if atual is None:
            linha.append(None)
            niveis.append(None)
            t += 1
            continue
        linha.append(atual.pid)
        niveis.append(nivel)
        restante[atual.pid] -= 1
        usado += 1
        if restante[atual.pid] == 0:
            atual = None
        elif usado == quanta[nivel]:
            filas[min(nivel + 1, ultimo)].append(atual)
            atual = None
        t += 1
    return metricas(procs, tuple(linha)), tuple(niveis)
