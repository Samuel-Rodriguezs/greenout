"""Triangulação de polígono simples por ear clipping, O(n^2)."""
from __future__ import annotations

from geo_orientacao import orientacao, sentido_poligono

Ponto = tuple[float, float]
Triangulo = tuple[Ponto, Ponto, Ponto]


def _dentro_ou_borda(p: Ponto, a: Ponto, b: Ponto, c: Ponto) -> bool:
    return (
        orientacao(a, b, p) >= 0 and orientacao(b, c, p) >= 0 and orientacao(c, a, p) >= 0
    )


def triangular(poligono: list[Ponto]) -> list[Triangulo]:
    """Triângulos (anti-horários) que cobrem o polígono simples dado.

    Aceita qualquer orientação. Sem vértices colineares o resultado tem n - 2
    triângulos; com colineares, a união continua cobrindo exatamente o polígono.
    Levanta ValueError se o polígono for degenerado ou não simples.
    """
    if sentido_poligono(poligono) == 0:
        raise ValueError("polígono degenerado (área nula)")
    v = list(poligono) if sentido_poligono(poligono) > 0 else list(reversed(poligono))
    triangulos: list[Triangulo] = []
    while len(v) > 3:
        n = len(v)
        achou = False
        for i in range(n):
            a, b, c = v[i - 1], v[i], v[(i + 1) % n]
            o = orientacao(a, b, c)
            if o == 0:  # vértice colinear: não gera triângulo, só some
                del v[i]
                achou = True
                break
            if o < 0:  # reflexo
                continue
            if any(
                q not in (a, b, c) and _dentro_ou_borda(q, a, b, c) for q in v
            ):
                continue
            triangulos.append((a, b, c))
            del v[i]
            achou = True
            break
        if not achou:
            raise ValueError("não foi possível triangular (polígono não simples?)")
    if len(v) == 3 and orientacao(*v) != 0:
        triangulos.append((v[0], v[1], v[2]))
    return triangulos
