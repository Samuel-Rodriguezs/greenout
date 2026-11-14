"""Menor caminho em labirinto com BFS."""

from collections import deque


def menor_caminho(labirinto: list[str]) -> int:
    """Menor número de passos de 'S' até 'E' (4 direções); '#' é parede; -1 se não há caminho."""
    inicio = fim = None
    for r, linha in enumerate(labirinto):
        for c, ch in enumerate(linha):
            if ch == "S":
                inicio = (r, c)
            elif ch == "E":
                fim = (r, c)
    if inicio is None or fim is None:
        raise ValueError("labirinto precisa ter 'S' e 'E'")
    visitados = {inicio}
    fila = deque([(inicio, 0)])
    while fila:
        (r, c), passos = fila.popleft()
        if (r, c) == fim:
            return passos
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < len(labirinto)
                and 0 <= nc < len(labirinto[nr])
                and labirinto[nr][nc] != "#"
                and (nr, nc) not in visitados
            ):
                visitados.add((nr, nc))
                fila.append(((nr, nc), passos + 1))
    return -1
