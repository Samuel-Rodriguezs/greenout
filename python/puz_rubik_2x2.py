"""Cubo de Rubik 2x2x2: modelo de permutações/orientações e solver IDA* com tabela de distâncias."""
from __future__ import annotations

from collections import deque
from typing import Optional

# Modelo: 8 cantos. Posição 7 (DBL) fica fixa, então só giramos U, R, F (quartos de volta).
# Estado = (permutação dos 8 cantos, orientações 0..2 dos 8 cantos).
# Posições: 0 UFL,1 UFR,2 UBR,3 UBL,4 DFL,5 DFR,6 DBR,7 DBL.
Estado = tuple[tuple[int, ...], tuple[int, ...]]

RESOLVIDO: Estado = (tuple(range(8)), (0,) * 8)

# Para cada movimento: ciclo de posições (a->b->c->d->a) e acréscimo de orientação por posição de destino.
_CICLOS = {
    "U": ((0, 1, 2, 3), (0, 0, 0, 0)),
    "R": ((1, 5, 6, 2), (1, 2, 1, 2)),
    "F": ((0, 4, 5, 1), (2, 1, 2, 1)),
}
MOVIMENTOS = ["U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'"]


def _quarto(estado: Estado, nome: str) -> Estado:
    ciclo, ori = _CICLOS[nome]
    perm, o = list(estado[0]), list(estado[1])
    novo_perm, novo_o = perm[:], o[:]
    for i in range(4):
        origem, destino = ciclo[i], ciclo[(i + 1) % 4]
        novo_perm[destino] = perm[origem]
        novo_o[destino] = (o[origem] + ori[i]) % 3
    return tuple(novo_perm), tuple(novo_o)


def aplicar(estado: Estado, mov: str) -> Estado:
    base = mov[0]
    vezes = 2 if mov.endswith("2") else 3 if mov.endswith("'") else 1
    for _ in range(vezes):
        estado = _quarto(estado, base)
    return estado


def aplicar_sequencia(estado: Estado, movs: list[str]) -> Estado:
    for m in movs:
        estado = aplicar(estado, m)
    return estado


def inverso(mov: str) -> str:
    if mov.endswith("2"):
        return mov
    return mov[0] if mov.endswith("'") else mov + "'"


def resolvido(estado: Estado) -> bool:
    return estado == RESOLVIDO


def valido(estado: Estado) -> bool:
    """Condições de alcançabilidade: permutação, soma das torções = 0 (mod 3), canto fixo no lugar."""
    perm, ori = estado
    return (sorted(perm) == list(range(8)) and all(0 <= o < 3 for o in ori)
            and sum(ori) % 3 == 0 and perm[7] == 7 and ori[7] == 0)


def _tabela_distancias(profundidade: int) -> dict[Estado, int]:
    dist = {RESOLVIDO: 0}
    fila = deque([RESOLVIDO])
    while fila:
        e = fila.popleft()
        if dist[e] == profundidade:
            continue
        for m in MOVIMENTOS:
            n = aplicar(e, m)
            if n not in dist:
                dist[n] = dist[e] + 1
                fila.append(n)
    return dist


_TABELA: Optional[dict[Estado, int]] = None
_PROF_TABELA = 5


def _tabela() -> dict[Estado, int]:
    global _TABELA
    if _TABELA is None:
        _TABELA = _tabela_distancias(_PROF_TABELA)
    return _TABELA


def resolver(estado: Estado, limite: int = 14) -> Optional[list[str]]:
    """IDA* com heurística admissível = distância exata (até a profundidade da tabela) ou profundidade+1."""
    if not valido(estado):
        return None
    tabela = _tabela()

    def h(e: Estado) -> int:
        return tabela.get(e, _PROF_TABELA + 1)

    caminho: list[str] = []

    def busca(e: Estado, g: int, teto: int, ultimo: str) -> bool:
        f = g + h(e)
        if f > teto:
            return False
        if e == RESOLVIDO:
            return True
        for m in MOVIMENTOS:
            if ultimo and m[0] == ultimo[0]:
                continue  # nunca dois giros seguidos da mesma face
            caminho.append(m)
            if busca(aplicar(e, m), g + 1, teto, m):
                return True
            caminho.pop()
        return False

    for teto in range(h(estado), limite + 1):
        if busca(estado, 0, teto, ""):
            return list(caminho)
    return None
