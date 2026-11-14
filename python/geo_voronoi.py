"""Diagrama de Voronoi por força bruta: cada célula é a caixa recortada por
semiplanos (bissetrizes), O(n^2 * k), com aritmética exata."""
from __future__ import annotations

from fractions import Fraction

Ponto = tuple[float, float]
PontoExato = tuple[Fraction, Fraction]


def _recortar(poligono: list[PontoExato], a: Fraction, b: Fraction, c: Fraction) -> list[PontoExato]:
    """Mantém a parte do polígono com a*x + b*y <= c (Sutherland-Hodgman)."""
    saida: list[PontoExato] = []
    n = len(poligono)
    for i in range(n):
        p, q = poligono[i], poligono[(i + 1) % n]
        vp = a * p[0] + b * p[1] - c
        vq = a * q[0] + b * q[1] - c
        if vp <= 0:
            saida.append(p)
        if (vp < 0 < vq) or (vq < 0 < vp):
            t = vp / (vp - vq)
            saida.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return saida


def celulas_voronoi(
    sitios: list[Ponto], caixa: tuple[float, float, float, float]
) -> list[list[PontoExato]]:
    """Polígono (anti-horário) da célula de cada sítio dentro da caixa.

    caixa = (xmin, ymin, xmax, ymax). Sítios duplicados levantam ValueError.
    A célula de um sítio fora da caixa pode sair vazia.
    """
    if len(set(sitios)) != len(sitios):
        raise ValueError("sítios duplicados")
    xmin, ymin, xmax, ymax = (Fraction(v) for v in caixa)
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("caixa inválida")
    base: list[PontoExato] = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    celulas = []
    for i, s in enumerate(sitios):
        sx, sy = Fraction(s[0]), Fraction(s[1])
        celula = base
        for j, t in enumerate(sitios):
            if i == j or not celula:
                continue
            tx, ty = Fraction(t[0]), Fraction(t[1])
            # |x-s|^2 <= |x-t|^2  <=>  2(t-s).x <= |t|^2 - |s|^2
            celula = _recortar(
                celula,
                2 * (tx - sx),
                2 * (ty - sy),
                tx * tx + ty * ty - sx * sx - sy * sy,
            )
        celulas.append(celula)
    return celulas


def sitio_mais_proximo(p: Ponto, sitios: list[Ponto]) -> int:
    """Índice do sítio cuja célula contém p (empates: menor índice)."""
    if not sitios:
        raise ValueError("sem sítios")
    return min(range(len(sitios)), key=lambda i: (p[0] - sitios[i][0]) ** 2 + (p[1] - sitios[i][1]) ** 2)
