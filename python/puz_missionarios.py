"""Missionários e canibais: BFS generalizado (n de cada, barco com capacidade k)."""
from __future__ import annotations

from collections import deque
from typing import Optional

# Estado: (missionários na margem esquerda, canibais na esquerda, barco na esquerda?)
Estado = tuple[int, int, bool]


def valido(m_esq: int, c_esq: int, n: int) -> bool:
    if not (0 <= m_esq <= n and 0 <= c_esq <= n):
        return False
    m_dir, c_dir = n - m_esq, n - c_esq
    return (m_esq == 0 or m_esq >= c_esq) and (m_dir == 0 or m_dir >= c_dir)


def sucessores(e: Estado, n: int, capacidade: int) -> list[tuple[tuple[int, int], Estado]]:
    m, c, barco = e
    sinal = -1 if barco else 1
    saida = []
    for dm in range(capacidade + 1):
        for dc in range(capacidade + 1 - dm):
            if dm + dc == 0:
                continue
            nm, nc = m + sinal * dm, c + sinal * dc
            if valido(nm, nc, n):
                saida.append(((dm, dc), (nm, nc, not barco)))
    return saida


def resolver(n: int = 3, capacidade: int = 2) -> Optional[list[tuple[int, int]]]:
    """Lista de travessias (missionários, canibais) ou None se for impossível."""
    if n < 0 or capacidade < 1:
        raise ValueError("parâmetros inválidos")
    if n == 0:
        return []
    inicial: Estado = (n, n, True)
    final: Estado = (0, 0, False)
    pai: dict[Estado, Optional[tuple[Estado, tuple[int, int]]]] = {inicial: None}
    fila = deque([inicial])
    while fila:
        atual = fila.popleft()
        if atual == final:
            passos = []
            while pai[atual] is not None:
                atual, mov = pai[atual]
                passos.append(mov)
            return passos[::-1]
        for mov, s in sucessores(atual, n, capacidade):
            if s not in pai:
                pai[s] = (atual, mov)
                fila.append(s)
    return None
