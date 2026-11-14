"""Travessia de ponte com lanterna: tempo mínimo (guloso ótimo) e solução por Dijkstra."""
from __future__ import annotations

import heapq
from typing import Optional


def tempo_minimo(tempos: list[int]) -> int:
    """Duas pessoas por vez, a lanterna volta com alguém. Recorrência clássica O(n log n)."""
    if any(t <= 0 for t in tempos):
        raise ValueError("tempos devem ser positivos")
    t = sorted(tempos)
    total = 0
    while len(t) > 3:
        a, b, y, z = t[0], t[1], t[-2], t[-1]
        total += min(b + a + z + b, z + a + y + a)
        t = t[:-2]
    if len(t) == 3:
        return total + t[0] + t[1] + t[2]
    if len(t) == 2:
        return total + t[1]
    if len(t) == 1:
        return total + t[0]
    return total


def solucao_dijkstra(tempos: list[int]) -> Optional[tuple[int, list[tuple[str, tuple[int, ...]]]]]:
    """Dijkstra no espaço (quem está na margem de origem, lado da lanterna).

    Retorna (tempo, passos), onde cada passo é ("ida"|"volta", tempos dos que cruzam).
    """
    n = len(tempos)
    if n == 0:
        return 0, []
    todos = (1 << n) - 1
    inicio = (todos, 0)  # máscara de quem ainda está na origem, lanterna na origem (0)
    dist = {inicio: 0}
    pai: dict = {}
    fila = [(0, inicio)]
    while fila:
        d, estado = heapq.heappop(fila)
        if d > dist[estado]:
            continue
        mascara, lado = estado
        if mascara == 0:
            passos = []
            while estado in pai:
                estado, passo = pai[estado]
                passos.append(passo)
            return d, passos[::-1]
        if lado == 0:
            pessoas = [i for i in range(n) if mascara >> i & 1]
            grupos = [(i,) for i in pessoas] + [(i, j) for k, i in enumerate(pessoas) for j in pessoas[k + 1:]]
        else:
            pessoas = [i for i in range(n) if not mascara >> i & 1]
            grupos = [(i,) for i in pessoas]
        for g in grupos:
            m = mascara
            for i in g:
                m ^= 1 << i
            custo = max(tempos[i] for i in g)
            novo = (m, 1 - lado)
            if d + custo < dist.get(novo, 1 << 60):
                dist[novo] = d + custo
                pai[novo] = (estado, ("ida" if lado == 0 else "volta", tuple(tempos[i] for i in g)))
                heapq.heappush(fila, (d + custo, novo))
    return None
