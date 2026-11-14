"""Ordenação topológica de tarefas com dependências (Kahn, desempate alfabético)."""

from __future__ import annotations

import heapq


class CicloDependenciaError(Exception):
    """Dependências formam um ciclo."""


def ordenar_tarefas(dependencias: dict[str, list[str]]) -> list[str]:
    """`dependencias[t]` lista as tarefas que devem rodar antes de t.

    Tarefas só citadas como dependência também entram na ordem.
    """
    tarefas: set[str] = set(dependencias)
    for deps in dependencias.values():
        tarefas.update(deps)
    grau = {t: 0 for t in tarefas}
    dependentes: dict[str, list[str]] = {t: [] for t in tarefas}
    for t, deps in dependencias.items():
        for d in set(deps):
            if d == t:
                raise CicloDependenciaError(f"tarefa depende de si mesma: {t}")
            grau[t] += 1
            dependentes[d].append(t)
    prontas = [t for t, g in grau.items() if g == 0]
    heapq.heapify(prontas)
    ordem: list[str] = []
    while prontas:
        t = heapq.heappop(prontas)
        ordem.append(t)
        for s in dependentes[t]:
            grau[s] -= 1
            if grau[s] == 0:
                heapq.heappush(prontas, s)
    if len(ordem) != len(tarefas):
        restantes = sorted(tarefas - set(ordem))
        raise CicloDependenciaError("ciclo envolvendo: " + ", ".join(restantes))
    return ordem


def niveis_paralelos(dependencias: dict[str, list[str]]) -> list[list[str]]:
    """Agrupa tarefas em rodadas que podem executar em paralelo."""
    ordem = ordenar_tarefas(dependencias)
    nivel: dict[str, int] = {}
    for t in ordem:
        nivel[t] = 1 + max((nivel[d] for d in dependencias.get(t, [])), default=-1)
    rodadas: list[list[str]] = [[] for _ in range(max(nivel.values(), default=-1) + 1)]
    for t in ordem:
        rodadas[nivel[t]].append(t)
    return rodadas
