"""Interseção de segmentos de reta com aritmética exata."""
from __future__ import annotations

from fractions import Fraction

from geo_orientacao import no_segmento, orientacao

Ponto = tuple[float, float]
PontoExato = tuple[Fraction, Fraction]


def segmentos_se_cruzam(p1: Ponto, p2: Ponto, p3: Ponto, p4: Ponto) -> bool:
    """True se os segmentos fechados p1p2 e p3p4 têm ao menos um ponto comum."""
    o1 = orientacao(p1, p2, p3)
    o2 = orientacao(p1, p2, p4)
    o3 = orientacao(p3, p4, p1)
    o4 = orientacao(p3, p4, p2)
    if o1 != o2 and o3 != o4:
        return True
    return (
        (o1 == 0 and no_segmento(p1, p2, p3))
        or (o2 == 0 and no_segmento(p1, p2, p4))
        or (o3 == 0 and no_segmento(p3, p4, p1))
        or (o4 == 0 and no_segmento(p3, p4, p2))
    )


def intersecao(
    p1: Ponto, p2: Ponto, p3: Ponto, p4: Ponto
) -> PontoExato | tuple[PontoExato, PontoExato] | None:
    """Ponto de interseção, ou None se disjuntos.

    Para segmentos colineares sobrepostos devolve (inicio, fim) do trecho comum;
    se tocam em um único ponto, devolve só esse ponto.
    """
    if not segmentos_se_cruzam(p1, p2, p3, p4):
        return None
    x1, y1, x2, y2 = (Fraction(v) for v in (*p1, *p2))
    x3, y3, x4, y4 = (Fraction(v) for v in (*p3, *p4))
    den = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if den != 0:
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    # paralelos que se tocam => colineares
    a = sorted([(x1, y1), (x2, y2)])
    b = sorted([(x3, y3), (x4, y4)])
    ini = max(a[0], b[0])
    fim = min(a[1], b[1])
    if ini == fim:
        return ini
    return (ini, fim)
