"""Jantar dos filósofos como simulação de eventos discretos (sem threads).

Estratégias:
- "ingenuo": pega o garfo esquerdo, depois o direito (há deadlock possível);
- "hierarquia": pega primeiro o garfo de menor número (quebra a espera circular);
- "garcom": no máximo n-1 filósofos sentados ao mesmo tempo.

Entre pegar o primeiro e o segundo garfo passa 1 unidade de tempo, o que
expõe a corrida que leva ao deadlock da estratégia ingênua.
"""
from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

ESTRATEGIAS = ("ingenuo", "hierarquia", "garcom")


@dataclass
class Resultado:
    estado: str  # "fim" ou "deadlock"
    fim: int
    refeicoes: list[int]
    bloqueados: list[int]
    intervalos: list[tuple[int, int, int]] = field(default_factory=list)  # (início, fim, filósofo)


def simular(
    n: int,
    estrategia: str,
    refeicoes: int = 1,
    t_pensar: int = 1,
    t_comer: int = 2,
) -> Resultado:
    if n < 2:
        raise ValueError("são necessários ao menos 2 filósofos")
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"estratégia desconhecida: {estrategia}")
    if min(refeicoes, t_pensar, t_comer) <= 0:
        raise ValueError("refeicoes e tempos devem ser positivos")

    dono: list[Optional[int]] = [None] * n
    espera: list[deque[tuple[int, int]]] = [deque() for _ in range(n)]  # (filósofo, etapa)
    fila_garcom: deque[int] = deque()
    sentados = 0
    comeu = [0] * n
    inicio_refeicao: dict[int, int] = {}
    intervalos: list[tuple[int, int, int]] = []
    eventos: list[tuple[int, int, str, int]] = []
    seq = 0
    fim = 0

    def agendar(t: int, tipo: str, i: int) -> None:
        nonlocal seq
        heapq.heappush(eventos, (t, seq, tipo, i))
        seq += 1

    def garfos(i: int) -> tuple[int, int]:
        esq, dir_ = i, (i + 1) % n
        return (min(esq, dir_), max(esq, dir_)) if estrategia == "hierarquia" else (esq, dir_)

    def pegar(t: int, i: int, etapa: int) -> None:
        g = garfos(i)[etapa]
        if dono[g] is None:
            dono[g] = i
            avancar(t, i, etapa)
        else:
            espera[g].append((i, etapa))

    def avancar(t: int, i: int, etapa: int) -> None:
        if etapa == 0:
            agendar(t + 1, "segundo", i)
        else:
            inicio_refeicao[i] = t
            agendar(t + t_comer, "fim_comer", i)

    def sentar(t: int, i: int) -> None:
        nonlocal sentados
        if estrategia == "garcom":
            if sentados >= n - 1:
                fila_garcom.append(i)
                return
            sentados += 1
        pegar(t, i, 0)

    agendar_inicial = [(t_pensar, "fome", i) for i in range(n)]
    for t, tipo, i in agendar_inicial:
        agendar(t, tipo, i)

    while eventos:
        t, _, tipo, i = heapq.heappop(eventos)
        fim = t
        if tipo == "fome":
            sentar(t, i)
        elif tipo == "segundo":
            pegar(t, i, 1)
        else:  # fim_comer
            comeu[i] += 1
            intervalos.append((inicio_refeicao.pop(i), t, i))
            for g in sorted(garfos(i)):
                dono[g] = None
                if espera[g]:
                    j, etapa = espera[g].popleft()
                    dono[g] = j
                    avancar(t, j, etapa)
            if estrategia == "garcom":
                sentados -= 1
                if fila_garcom:
                    sentar(t, fila_garcom.popleft())
            if comeu[i] < refeicoes:
                agendar(t + t_pensar, "fome", i)

    bloqueados = sorted(
        {j for q in espera for j, _ in q} | set(fila_garcom)
    )
    estado = "deadlock" if bloqueados else "fim"
    return Resultado(estado, fim, comeu, bloqueados, sorted(intervalos))
