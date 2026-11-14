"""Passeio do cavalo com a heurística de Warnsdorff (e variante fechada via backtracking)."""
from __future__ import annotations

from typing import Optional

Casa = tuple[int, int]
SALTOS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


def movimentos(casa: Casa, n: int, visitadas: set[Casa]) -> list[Casa]:
    r, c = casa
    return [(r + dr, c + dc) for dr, dc in SALTOS
            if 0 <= r + dr < n and 0 <= c + dc < n and (r + dr, c + dc) not in visitadas]


def passeio_warnsdorff(n: int, inicio: Casa = (0, 0)) -> Optional[list[Casa]]:
    """Percorre sempre a casa com menos saídas; desempate pela ordem fixa dos saltos.

    Retorna o caminho ou None se a heurística falhar (ou n sem passeio possível).
    """
    if not (0 <= inicio[0] < n and 0 <= inicio[1] < n):
        raise ValueError("início fora do tabuleiro")
    caminho = [inicio]
    visitadas = {inicio}
    while len(caminho) < n * n:
        opcoes = movimentos(caminho[-1], n, visitadas)
        if not opcoes:
            return None
        prox = min(opcoes, key=lambda p: len(movimentos(p, n, visitadas | {p})))
        caminho.append(prox)
        visitadas.add(prox)
    return caminho


def passeio_backtracking(n: int, inicio: Casa = (0, 0), fechado: bool = False) -> Optional[list[Casa]]:
    """Busca exaustiva ordenada por Warnsdorff; com fechado=True exige voltar ao início."""
    if fechado and (n * n) % 2 == 1:
        return None  # o grafo do cavalo é bipartido: ciclo exige nº par de casas
    caminho = [inicio]
    visitadas = {inicio}

    def passo() -> bool:
        if len(caminho) == n * n:
            if not fechado:
                return True
            r, c = caminho[-1]
            return (inicio[0] - r, inicio[1] - c) in SALTOS
        if fechado and not _poda_ok(caminho[-1], inicio, n, visitadas):
            return False
        opcoes = sorted(movimentos(caminho[-1], n, visitadas),
                        key=lambda p: len(movimentos(p, n, visitadas | {p})))
        for p in opcoes:
            caminho.append(p)
            visitadas.add(p)
            if passo():
                return True
            caminho.pop()
            visitadas.discard(p)
        return False

    return caminho if passo() else None


def _poda_ok(cabeca: Casa, inicio: Casa, n: int, visitadas: set[Casa]) -> bool:
    """Toda casa livre precisa de 2 vizinhas aproveitáveis (livres, cabeça ou início)."""
    for r in range(n):
        for c in range(n):
            if (r, c) in visitadas:
                continue
            uteis = 0
            for dr, dc in SALTOS:
                v = (r + dr, c + dc)
                if 0 <= v[0] < n and 0 <= v[1] < n and (v not in visitadas or v in (cabeca, inicio)):
                    uteis += 1
            if uteis < 2:
                return False
    return True


def valido(caminho: list[Casa], n: int) -> bool:
    if len(caminho) != n * n or len(set(caminho)) != n * n:
        return False
    return all((b[0] - a[0], b[1] - a[1]) in SALTOS for a, b in zip(caminho, caminho[1:]))
