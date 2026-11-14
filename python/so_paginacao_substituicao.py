"""Algoritmos de substituição de páginas: FIFO, LRU, Ótimo, Clock e LFU.

Os quadros são posições fixas; páginas novas ocupam o primeiro quadro livre
(menor índice) e só depois se escolhe uma vítima. Inclui a demonstração da
anomalia de Belady (FIFO pode ter mais faltas com mais quadros).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

POLITICAS = ("fifo", "lru", "otimo", "clock", "lfu")


@dataclass(frozen=True)
class Resultado:
    politica: str
    faltas: int
    acertos: int
    houve_falta: tuple[bool, ...]
    quadros: tuple[tuple[Optional[int], ...], ...]  # estado após cada referência

    @property
    def taxa_faltas(self) -> float:
        total = self.faltas + self.acertos
        return self.faltas / total if total else 0.0


def _vitima(
    politica: str,
    t: int,
    refs: Sequence[int],
    quadros: list[Optional[int]],
    carga: list[int],
    ultimo: list[int],
    freq: list[int],
    bits: list[int],
    mao: list[int],
) -> int:
    n = len(quadros)
    if politica == "fifo":
        return min(range(n), key=lambda i: carga[i])
    if politica == "lru":
        return min(range(n), key=lambda i: ultimo[i])
    if politica == "lfu":
        return min(range(n), key=lambda i: (freq[i], carga[i]))
    if politica == "otimo":
        def proximo_uso(i: int) -> float:
            for k in range(t + 1, len(refs)):
                if refs[k] == quadros[i]:
                    return k
            return float("inf")

        return max(range(n), key=lambda i: (proximo_uso(i), -i))
    # clock / segunda chance
    while True:
        i = mao[0]
        if bits[i] == 0:
            mao[0] = (i + 1) % n
            return i
        bits[i] = 0
        mao[0] = (i + 1) % n


def simular(refs: Sequence[int], nquadros: int, politica: str) -> Resultado:
    if politica not in POLITICAS:
        raise ValueError(f"política desconhecida: {politica}")
    if nquadros <= 0:
        raise ValueError("nquadros deve ser positivo")
    quadros: list[Optional[int]] = [None] * nquadros
    carga = [0] * nquadros
    ultimo = [0] * nquadros
    freq = [0] * nquadros
    bits = [0] * nquadros
    mao = [0]
    faltas = 0
    flags: list[bool] = []
    estados: list[tuple[Optional[int], ...]] = []
    for t, pag in enumerate(refs):
        if pag in quadros:
            i = quadros.index(pag)
            flags.append(False)
        else:
            faltas += 1
            flags.append(True)
            if None in quadros:
                i = quadros.index(None)
            else:
                i = _vitima(politica, t, refs, quadros, carga, ultimo, freq, bits, mao)
            quadros[i] = pag
            carga[i] = t
            freq[i] = 0
        ultimo[i] = t
        freq[i] += 1
        bits[i] = 1
        estados.append(tuple(quadros))
    return Resultado(politica, faltas, len(refs) - faltas, tuple(flags), tuple(estados))


def faltas_por_quadros(refs: Sequence[int], politica: str, maximo: int) -> list[tuple[int, int]]:
    return [(n, simular(refs, n, politica).faltas) for n in range(1, maximo + 1)]


def anomalia_belady(
    refs: Sequence[int], politica: str = "fifo", maximo: int = 8
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Pares ((n, faltas), (n+1, faltas')) em que mais quadros causaram mais faltas."""
    serie = faltas_por_quadros(refs, politica, maximo)
    return [(a, b) for a, b in zip(serie, serie[1:]) if b[1] > a[1]]
