"""Sweep line para interseções de segmentos.

Varre os eventos por x mantendo os segmentos ativos; cada segmento só é testado
contra os que se sobrepõem a ele em x (em vez de todos os pares). Pior caso O(n^2),
mas bem melhor que a força bruta quando os segmentos são curtos/espalhados.
"""
from __future__ import annotations

from geo_segmentos import segmentos_se_cruzam

Ponto = tuple[float, float]
Segmento = tuple[Ponto, Ponto]


def _normalizar(s: Segmento) -> Segmento:
    return (s[0], s[1]) if s[0] <= s[1] else (s[1], s[0])


def pares_que_se_cruzam(segmentos: list[Segmento]) -> list[tuple[int, int]]:
    """Pares (i, j), i < j, de segmentos com ao menos um ponto em comum."""
    segs = [_normalizar(s) for s in segmentos]
    eventos: list[tuple[float, int, int]] = []  # (x, tipo, índice); 0 = entra, 1 = sai
    for i, (a, b) in enumerate(segs):
        eventos.append((a[0], 0, i))
        eventos.append((b[0], 1, i))
    eventos.sort()
    ativos: set[int] = set()
    achados: list[tuple[int, int]] = []
    for _, tipo, i in eventos:
        if tipo == 0:
            for j in ativos:
                if segmentos_se_cruzam(*segs[i], *segs[j]):
                    achados.append((min(i, j), max(i, j)))
            ativos.add(i)
        else:
            ativos.discard(i)
    return sorted(achados)


def existe_intersecao(segmentos: list[Segmento]) -> bool:
    """True assim que um par se cruza (interrompe a varredura cedo)."""
    segs = [_normalizar(s) for s in segmentos]
    eventos = sorted(
        [(a[0], 0, i) for i, (a, _) in enumerate(segs)]
        + [(b[0], 1, i) for i, (_, b) in enumerate(segs)]
    )
    ativos: set[int] = set()
    for _, tipo, i in eventos:
        if tipo == 0:
            if any(segmentos_se_cruzam(*segs[i], *segs[j]) for j in ativos):
                return True
            ativos.add(i)
        else:
            ativos.discard(i)
    return False
