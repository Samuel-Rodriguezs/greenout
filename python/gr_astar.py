"""A* em grade com movimentos 4-direcionais e heurística de Manhattan."""

from __future__ import annotations

import heapq

Ponto = tuple[int, int]


def astar(grade: list[str], inicio: Ponto, fim: Ponto, parede: str = "#") -> list[Ponto] | None:
    """Menor caminho (lista de pontos) ou None. Células com `parede` são bloqueadas."""
    linhas = len(grade)
    colunas = len(grade[0]) if linhas else 0

    def livre(p: Ponto) -> bool:
        return 0 <= p[0] < linhas and 0 <= p[1] < colunas and grade[p[0]][p[1]] != parede

    if not livre(inicio) or not livre(fim):
        return None

    def h(p: Ponto) -> int:
        return abs(p[0] - fim[0]) + abs(p[1] - fim[1])

    g = {inicio: 0}
    pai: dict[Ponto, Ponto] = {}
    heap = [(h(inicio), 0, inicio)]
    fechado: set[Ponto] = set()
    while heap:
        _, custo, atual = heapq.heappop(heap)
        if atual in fechado:
            continue
        if atual == fim:
            caminho = [atual]
            while atual in pai:
                atual = pai[atual]
                caminho.append(atual)
            return caminho[::-1]
        fechado.add(atual)
        for dl, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            viz = (atual[0] + dl, atual[1] + dc)
            if not livre(viz) or viz in fechado:
                continue
            novo = custo + 1
            if novo < g.get(viz, float("inf")):
                g[viz] = novo
                pai[viz] = atual
                heapq.heappush(heap, (novo + h(viz), novo, viz))
    return None
