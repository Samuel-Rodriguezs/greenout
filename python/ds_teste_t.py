"""Teste t de Student para duas amostras (Welch e variâncias iguais) e distribuição t."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


def _betacf(a: float, b: float, x: float) -> float:
    fpmin = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c = 1.0
    d = 1 - qab * x / qap
    d = 1 / (d if abs(d) > fpmin else fpmin)
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = d if abs(d) > fpmin else fpmin
        c = 1 + aa / c
        c = c if abs(c) > fpmin else fpmin
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = d if abs(d) > fpmin else fpmin
        c = 1 + aa / c
        c = c if abs(c) > fpmin else fpmin
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 3e-15:
            break
    return h


def beta_incompleta(a: float, b: float, x: float) -> float:
    """Função beta incompleta regularizada I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, gl: float) -> float:
    if gl <= 0:
        raise ValueError("graus de liberdade devem ser positivos")
    if t == 0:
        return 0.5
    i = beta_incompleta(gl / 2, 0.5, gl / (gl + t * t))
    return 1 - 0.5 * i if t > 0 else 0.5 * i


def t_ppf(p: float, gl: float) -> float:
    """Quantil da t de Student por bisseção."""
    if not 0 < p < 1:
        raise ValueError("p deve estar em (0, 1)")
    lo, hi = -1e6, 1e6
    for _ in range(300):
        mid = (lo + hi) / 2
        if t_cdf(mid, gl) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


@dataclass(frozen=True)
class ResultadoT:
    t: float
    gl: float
    p_valor: float


def _media_var(x: Sequence[float]) -> tuple[float, float]:
    if len(x) < 2:
        raise ValueError("cada amostra precisa de ao menos 2 observações")
    m = sum(x) / len(x)
    return m, sum((v - m) ** 2 for v in x) / (len(x) - 1)


def _resultado(t: float, gl: float) -> ResultadoT:
    return ResultadoT(t, gl, 2 * (1 - t_cdf(abs(t), gl)))


def t_welch(a: Sequence[float], b: Sequence[float]) -> ResultadoT:
    ma, va = _media_var(a)
    mb, vb = _media_var(b)
    ea, eb = va / len(a), vb / len(b)
    if ea + eb == 0:
        raise ValueError("variância nula nas duas amostras")
    t = (ma - mb) / math.sqrt(ea + eb)
    gl = (ea + eb) ** 2 / ((ea ** 2) / (len(a) - 1) + (eb ** 2) / (len(b) - 1))
    return _resultado(t, gl)


def t_student(a: Sequence[float], b: Sequence[float]) -> ResultadoT:
    """Teste t com variância combinada (assume variâncias iguais)."""
    ma, va = _media_var(a)
    mb, vb = _media_var(b)
    na, nb = len(a), len(b)
    gl = na + nb - 2
    sp2 = ((na - 1) * va + (nb - 1) * vb) / gl
    if sp2 == 0:
        raise ValueError("variância nula nas duas amostras")
    t = (ma - mb) / math.sqrt(sp2 * (1 / na + 1 / nb))
    return _resultado(t, gl)
