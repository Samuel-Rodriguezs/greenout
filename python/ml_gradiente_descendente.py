"""Gradiente descendente genérico para funções convexas (com momento opcional)."""
from __future__ import annotations

from typing import Callable

Vetor = list[float]


def gradiente_numerico(f: Callable[[Vetor], float], x: Vetor, h: float = 1e-6) -> Vetor:
    """Gradiente por diferenças centrais."""
    g = []
    for i in range(len(x)):
        mais = list(x)
        menos = list(x)
        mais[i] += h
        menos[i] -= h
        g.append((f(mais) - f(menos)) / (2 * h))
    return g


def descer(
    f: Callable[[Vetor], float],
    inicio: Vetor,
    grad: Callable[[Vetor], Vetor] | None = None,
    taxa: float = 0.1,
    momento: float = 0.0,
    max_iter: int = 10000,
    tol: float = 1e-8,
) -> tuple[Vetor, int]:
    """Retorna (mínimo encontrado, iterações). Para quando a norma do gradiente < tol."""
    if taxa <= 0:
        raise ValueError("taxa deve ser positiva")
    g_fn = grad if grad is not None else (lambda p: gradiente_numerico(f, p))
    x = list(inicio)
    v = [0.0] * len(x)
    for it in range(1, max_iter + 1):
        g = g_fn(x)
        if sum(c * c for c in g) ** 0.5 < tol:
            return x, it
        for i in range(len(x)):
            v[i] = momento * v[i] - taxa * g[i]
            x[i] += v[i]
    return x, max_iter
