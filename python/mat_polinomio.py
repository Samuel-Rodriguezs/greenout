"""Polinômios com coeficientes em ordem crescente de grau: [a0, a1, a2, ...]."""
from typing import List, Sequence


def normalizar(p: Sequence[float]) -> List[float]:
    r = list(p)
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r or [0]


def grau(p: Sequence[float]) -> int:
    return len(normalizar(p)) - 1


def somar(p: Sequence[float], q: Sequence[float]) -> List[float]:
    n = max(len(p), len(q))
    return normalizar([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0)
                       for i in range(n)])


def multiplicar(p: Sequence[float], q: Sequence[float]) -> List[float]:
    if not p or not q:
        return [0]
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return normalizar(r)


def avaliar(p: Sequence[float], x: float) -> float:
    """Avaliação pelo método de Horner."""
    r = 0
    for c in reversed(p):
        r = r * x + c
    return r


def derivar(p: Sequence[float]) -> List[float]:
    if len(p) <= 1:
        return [0]
    return normalizar([i * c for i, c in enumerate(p)][1:])
