"""Método da bisseção para raízes de funções contínuas."""
from typing import Callable


def bissecao(f: Callable[[float], float], a: float, b: float,
             tol: float = 1e-12, max_iter: int = 200) -> float:
    """Raiz de f em [a, b]; exige sinais opostos nas extremidades."""
    fa, fb = f(a), f(b)
    if fa == 0:
        return a
    if fb == 0:
        return b
    if fa * fb > 0:
        raise ValueError("f(a) e f(b) devem ter sinais opostos")
    for _ in range(max_iter):
        m = (a + b) / 2
        fm = f(m)
        if fm == 0 or (b - a) / 2 < tol:
            return m
        if fa * fm < 0:
            b = m
        else:
            a, fa = m, fm
    return (a + b) / 2
