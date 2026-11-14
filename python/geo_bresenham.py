"""Algoritmo de Bresenham e linha de visão em grades."""
from __future__ import annotations

Celula = tuple[int, int]  # (linha, coluna)


def linha(a: Celula, b: Celula) -> list[Celula]:
    """Células da reta de a até b (ambas inclusas), em todos os octantes."""
    (r0, c0), (r1, c1) = a, b
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr = 1 if r1 > r0 else -1
    sc = 1 if c1 > c0 else -1
    erro = dc - dr
    celulas = []
    r, c = r0, c0
    while True:
        celulas.append((r, c))
        if (r, c) == (r1, c1):
            return celulas
        e2 = 2 * erro
        if e2 > -dr:
            erro -= dr
            c += sc
        if e2 < dc:
            erro += dc
            r += sr


def tem_linha_de_visao(grade: list[str], a: Celula, b: Celula, parede: str = "#") -> bool:
    """True se nenhuma célula entre a e b (exclusive extremos) é parede.

    As extremidades não bloqueiam: dá para ver uma parede de frente. Células
    fora da grade levantam IndexError.
    """
    for r, c in (a, b):
        if not (0 <= r < len(grade) and 0 <= c < len(grade[r])):
            raise IndexError(f"célula fora da grade: {(r, c)}")
    for r, c in linha(a, b)[1:-1]:
        if not (0 <= r < len(grade) and 0 <= c < len(grade[r])):
            raise IndexError(f"célula fora da grade: {(r, c)}")
        if grade[r][c] == parede:
            return False
    return True


def celulas_visiveis(grade: list[str], origem: Celula, alcance: int, parede: str = "#") -> set[Celula]:
    """Células visíveis de origem num raio de Chebyshev `alcance` (inclui a origem)."""
    r0, c0 = origem
    visiveis = set()
    for r in range(max(0, r0 - alcance), min(len(grade), r0 + alcance + 1)):
        for c in range(max(0, c0 - alcance), min(len(grade[r]), c0 + alcance + 1)):
            if tem_linha_de_visao(grade, origem, (r, c), parede):
                visiveis.add((r, c))
    return visiveis
