"""Desfoque (blur) por média (caixa) e gaussiano."""

import math

from img_convolucao import convolver, limitar

Imagem = list[list[int]]


def kernel_caixa(raio: int) -> list[list[float]]:
    n = 2 * raio + 1
    return [[1.0] * n for _ in range(n)]


def kernel_gaussiano(raio: int, sigma: float) -> list[list[float]]:
    """Kernel (2r+1)x(2r+1) normalizado para somar 1."""
    if sigma <= 0:
        raise ValueError("sigma deve ser positivo")
    pesos = [[math.exp(-(x * x + y * y) / (2 * sigma * sigma))
              for x in range(-raio, raio + 1)] for y in range(-raio, raio + 1)]
    total = sum(sum(l) for l in pesos)
    return [[p / total for p in l] for l in pesos]


def blur_caixa(imagem: Imagem, raio: int = 1, borda: str = "replicar") -> Imagem:
    if raio < 1:
        raise ValueError("raio deve ser >= 1")
    n = 2 * raio + 1
    return limitar(convolver(imagem, kernel_caixa(raio), borda, n * n))


def blur_gaussiano(imagem: Imagem, raio: int = 1, sigma: float = 1.0,
                   borda: str = "replicar") -> Imagem:
    if raio < 1:
        raise ValueError("raio deve ser >= 1")
    return limitar(convolver(imagem, kernel_gaussiano(raio, sigma), borda))
