"""Filtros FIR por janelamento (passa-baixa, passa-alta, passa-banda)."""
from __future__ import annotations

import math

from sig_janelas import hamming


def _sinc(x: float) -> float:
    return 1.0 if x == 0 else math.sin(math.pi * x) / (math.pi * x)


def _validar(ntaps: int, taxa: float, *cortes: float) -> None:
    if ntaps < 1 or ntaps % 2 == 0:
        raise ValueError("ntaps deve ser ímpar e positivo")
    if taxa <= 0:
        raise ValueError("taxa deve ser positiva")
    for c in cortes:
        if not 0 < c < taxa / 2:
            raise ValueError("corte deve estar entre 0 e taxa/2")


def passa_baixa(corte: float, taxa: float, ntaps: int, janela=hamming) -> list[float]:
    """Resposta ao impulso sinc janelada, com ganho DC normalizado para 1."""
    _validar(ntaps, taxa, corte)
    fc = corte / taxa
    meio = (ntaps - 1) // 2
    w = janela(ntaps)
    h = [2 * fc * _sinc(2 * fc * (i - meio)) * w[i] for i in range(ntaps)]
    soma = sum(h)
    return [v / soma for v in h]


def passa_alta(corte: float, taxa: float, ntaps: int, janela=hamming) -> list[float]:
    """Inversão espectral do passa-baixa."""
    h = [-v for v in passa_baixa(corte, taxa, ntaps, janela)]
    h[(ntaps - 1) // 2] += 1.0
    return h


def passa_banda(f1: float, f2: float, taxa: float, ntaps: int, janela=hamming) -> list[float]:
    """Diferença de dois passa-baixa (f1 < f2)."""
    if f1 >= f2:
        raise ValueError("f1 deve ser menor que f2")
    a = passa_baixa(f2, taxa, ntaps, janela)
    b = passa_baixa(f1, taxa, ntaps, janela)
    return [x - y for x, y in zip(a, b)]


def filtrar(x: list[float], h: list[float]) -> list[float]:
    """Aplica o FIR causal; saída com o tamanho de x (atraso (ntaps-1)/2)."""
    return [
        sum(h[k] * x[n - k] for k in range(len(h)) if n - k >= 0)
        for n in range(len(x))
    ]


def resposta_em_frequencia(h: list[float], freq: float, taxa: float) -> float:
    """|H(f)| do filtro na frequência dada."""
    w = 2 * math.pi * freq / taxa
    re = sum(c * math.cos(w * k) for k, c in enumerate(h))
    im = sum(-c * math.sin(w * k) for k, c in enumerate(h))
    return math.hypot(re, im)
