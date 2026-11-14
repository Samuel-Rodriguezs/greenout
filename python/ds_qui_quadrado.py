"""Teste qui-quadrado: aderência e independência (tabela de contingência)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


def _gser(a: float, x: float) -> float:
    ap, soma = a, 1 / a
    delta = soma
    for _ in range(1000):
        ap += 1
        delta *= x / ap
        soma += delta
        if abs(delta) < abs(soma) * 1e-15:
            break
    return soma * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a: float, x: float) -> float:
    fpmin = 1e-300
    b = x + 1 - a
    c = 1 / fpmin
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = d if abs(d) > fpmin else fpmin
        c = b + an / c
        c = c if abs(c) > fpmin else fpmin
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def qui2_sf(x: float, gl: int) -> float:
    """P(X >= x) para qui-quadrado com gl graus de liberdade."""
    if gl <= 0:
        raise ValueError("gl deve ser positivo")
    if x <= 0:
        return 1.0
    a = gl / 2
    if x < a + 1:
        return 1 - _gser(a, x / 2)
    return _gcf(a, x / 2)


@dataclass(frozen=True)
class ResultadoQui2:
    estatistica: float
    gl: int
    p_valor: float


def aderencia(observado: Sequence[float], esperado: Sequence[float]) -> ResultadoQui2:
    if len(observado) != len(esperado) or len(observado) < 2:
        raise ValueError("listas devem ter o mesmo tamanho (>= 2)")
    if any(e <= 0 for e in esperado):
        raise ValueError("frequências esperadas devem ser positivas")
    if abs(sum(observado) - sum(esperado)) > 1e-9 * max(1.0, sum(esperado)):
        raise ValueError("somas de observado e esperado diferem")
    chi = sum((o - e) ** 2 / e for o, e in zip(observado, esperado))
    gl = len(observado) - 1
    return ResultadoQui2(chi, gl, qui2_sf(chi, gl))


def esperados_independencia(tabela: Sequence[Sequence[float]]) -> list[list[float]]:
    linhas = [sum(l) for l in tabela]
    colunas = [sum(l[j] for l in tabela) for j in range(len(tabela[0]))]
    total = sum(linhas)
    return [[li * cj / total for cj in colunas] for li in linhas]


def independencia(tabela: Sequence[Sequence[float]]) -> ResultadoQui2:
    if len(tabela) < 2 or len(tabela[0]) < 2:
        raise ValueError("tabela deve ser ao menos 2x2")
    if any(len(l) != len(tabela[0]) for l in tabela):
        raise ValueError("linhas de tamanhos diferentes")
    if any(sum(l) == 0 for l in tabela) or any(sum(l[j] for l in tabela) == 0 for j in range(len(tabela[0]))):
        raise ValueError("linha ou coluna sem observações")
    esp = esperados_independencia(tabela)
    chi = sum((o - e) ** 2 / e for lo, le in zip(tabela, esp) for o, e in zip(lo, le))
    gl = (len(tabela) - 1) * (len(tabela[0]) - 1)
    return ResultadoQui2(chi, gl, qui2_sf(chi, gl))
