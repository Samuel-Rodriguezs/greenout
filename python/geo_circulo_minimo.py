"""Menor círculo envolvente (algoritmo de Welzl, versão iterativa), O(n) esperado."""
from __future__ import annotations

import math
import random

Ponto = tuple[float, float]
Circulo = tuple[float, float, float]  # (cx, cy, raio)
EPS = 1e-9


def _de_dois(a: Ponto, b: Ponto) -> Circulo:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, math.dist(a, b) / 2)


def _de_tres(a: Ponto, b: Ponto, c: Ponto) -> Circulo | None:
    """Circunscrito ao triângulo; None se colineares."""
    bx, by = b[0] - a[0], b[1] - a[1]
    cx, cy = c[0] - a[0], c[1] - a[1]
    d = 2 * (bx * cy - by * cx)
    if d == 0:
        return None
    ux = (cy * (bx * bx + by * by) - by * (cx * cx + cy * cy)) / d
    uy = (bx * (cx * cx + cy * cy) - cx * (bx * bx + by * by)) / d
    return (a[0] + ux, a[1] + uy, math.hypot(ux, uy))


def _contem(c: Circulo, p: Ponto) -> bool:
    return math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + EPS


def circulo_minimo(pontos: list[Ponto], semente: int | None = 0) -> Circulo:
    """Devolve (cx, cy, r) do menor círculo que contém todos os pontos."""
    if not pontos:
        raise ValueError("sem pontos")
    pts = list(pontos)
    random.Random(semente).shuffle(pts)
    c: Circulo = (pts[0][0], pts[0][1], 0.0)
    for i, p in enumerate(pts):
        if _contem(c, p):
            continue
        c = (p[0], p[1], 0.0)
        for j in range(i):
            q = pts[j]
            if _contem(c, q):
                continue
            c = _de_dois(p, q)
            for k in range(j):
                r = pts[k]
                if _contem(c, r):
                    continue
                tres = _de_tres(p, q, r)
                if tres is None:
                    # colineares: o círculo é o de diâmetro maior
                    c = max((_de_dois(p, q), _de_dois(p, r), _de_dois(q, r)), key=lambda t: t[2])
                else:
                    c = tres
    return c
