"""Operações com matrizes (listas de listas) e eliminação de Gauss."""
from typing import List

Matriz = List[List[float]]
_EPS = 1e-12


def transposta(m: Matriz) -> Matriz:
    return [list(l) for l in zip(*m)]


def multiplicar(a: Matriz, b: Matriz) -> Matriz:
    if len(a[0]) != len(b):
        raise ValueError("dimensões incompatíveis")
    bt = transposta(b)
    return [[sum(x * y for x, y in zip(l, c)) for c in bt] for l in a]


def identidade(n: int) -> Matriz:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _quadrada(m: Matriz) -> None:
    if not m or any(len(l) != len(m) for l in m):
        raise ValueError("matriz deve ser quadrada")


def determinante(m: Matriz) -> float:
    """Determinante por eliminação de Gauss com pivotamento parcial."""
    _quadrada(m)
    a = [list(map(float, l)) for l in m]
    n, det = len(a), 1.0
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[p][i]) < _EPS:
            return 0.0
        if p != i:
            a[i], a[p] = a[p], a[i]
            det = -det
        det *= a[i][i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= f * a[i][c]
    return det


def inversa(m: Matriz) -> Matriz:
    """Inversa por Gauss-Jordan."""
    _quadrada(m)
    n = len(m)
    a = [list(map(float, l)) + idl for l, idl in zip(m, identidade(n))]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[p][i]) < _EPS:
            raise ValueError("matriz singular")
        a[i], a[p] = a[p], a[i]
        piv = a[i][i]
        a[i] = [x / piv for x in a[i]]
        for r in range(n):
            if r != i:
                f = a[r][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    return [l[n:] for l in a]


def resolver_sistema(a: Matriz, b: List[float]) -> List[float]:
    """Resolve A x = b."""
    _quadrada(a)
    if len(b) != len(a):
        raise ValueError("tamanho de b incompatível")
    inv = inversa(a)
    return [sum(x * y for x, y in zip(l, b)) for l in inv]
