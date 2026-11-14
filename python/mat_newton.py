"""Método de Newton-Raphson para raízes de funções reais."""
from typing import Callable


def newton(f: Callable[[float], float], df: Callable[[float], float], x0: float,
           tol: float = 1e-12, max_iter: int = 100) -> float:
    """Encontra uma raiz de f partindo de x0 usando a derivada df."""
    x = x0
    for _ in range(max_iter):
        d = df(x)
        if d == 0:
            raise ZeroDivisionError("derivada nula durante a iteração")
        passo = f(x) / d
        x -= passo
        if abs(passo) < tol:
            return x
    raise RuntimeError("Newton não convergiu")


def raiz_quadrada(n: float) -> float:
    """Raiz quadrada de n >= 0 via Newton."""
    if n < 0:
        raise ValueError("n deve ser não negativo")
    if n == 0:
        return 0.0
    return newton(lambda x: x * x - n, lambda x: 2 * x, max(n, 1.0))
