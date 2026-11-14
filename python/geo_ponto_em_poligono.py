"""Ponto em polígono: ray casting e número de enrolamento (winding number)."""
from __future__ import annotations

from geo_orientacao import no_segmento, orientacao

Ponto = tuple[float, float]

DENTRO = 1
FRONTEIRA = 0
FORA = -1


def _na_fronteira(p: Ponto, poligono: list[Ponto]) -> bool:
    n = len(poligono)
    return any(no_segmento(poligono[i], poligono[(i + 1) % n], p) for i in range(n))


def ray_casting(p: Ponto, poligono: list[Ponto]) -> int:
    """DENTRO (1), FRONTEIRA (0) ou FORA (-1), traçando um raio para +x."""
    if len(poligono) < 3:
        return FRONTEIRA if _na_fronteira(p, poligono) else FORA
    if _na_fronteira(p, poligono):
        return FRONTEIRA
    x, y = p
    dentro = False
    n = len(poligono)
    for i in range(n):
        (x1, y1), (x2, y2) = poligono[i], poligono[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            # o cruzamento está à direita de p?
            o = orientacao((x1, y1), (x2, y2), p)
            if (o > 0) == (y2 > y1):
                dentro = not dentro
    return DENTRO if dentro else FORA


def winding_number(p: Ponto, poligono: list[Ponto]) -> int:
    """Número de voltas do polígono em torno de p (0 se fora; sinal = sentido).

    Para ponto na fronteira o valor não é significativo; use classificar().
    """
    wn = 0
    n = len(poligono)
    for i in range(n):
        a, b = poligono[i], poligono[(i + 1) % n]
        if a[1] <= p[1]:
            if b[1] > p[1] and orientacao(a, b, p) > 0:
                wn += 1
        elif b[1] <= p[1] and orientacao(a, b, p) < 0:
            wn -= 1
    return wn


def classificar(p: Ponto, poligono: list[Ponto]) -> int:
    """Classificação por winding number, tratando a fronteira explicitamente."""
    if _na_fronteira(p, poligono):
        return FRONTEIRA
    return DENTRO if winding_number(p, poligono) != 0 else FORA
