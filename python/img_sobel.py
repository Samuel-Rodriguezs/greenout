"""Detecção de bordas por gradiente: operadores de Sobel e Prewitt."""

import math

from img_convolucao import correlacionar, limitar

Imagem = list[list[int]]
Matriz = list[list[float]]

_KERNELS = {
    "sobel": ([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
              [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]),
    "prewitt": ([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
                [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]),
}


def gradientes(imagem: Imagem, operador: str = "sobel",
               borda: str = "replicar") -> tuple[Matriz, Matriz]:
    """Retorna (gx, gy); gx cresce para a direita e gy para baixo."""
    if operador not in _KERNELS:
        raise ValueError(f"operador desconhecido: {operador}")
    kx, ky = _KERNELS[operador]
    return correlacionar(imagem, kx, borda), correlacionar(imagem, ky, borda)


def magnitude(imagem: Imagem, operador: str = "sobel") -> Matriz:
    gx, gy = gradientes(imagem, operador)
    return [[math.hypot(a, b) for a, b in zip(lx, ly)] for lx, ly in zip(gx, gy)]


def direcao(imagem: Imagem, operador: str = "sobel") -> Matriz:
    """Ângulo do gradiente em radianos, em (-pi, pi]."""
    gx, gy = gradientes(imagem, operador)
    return [[math.atan2(b, a) for a, b in zip(lx, ly)] for lx, ly in zip(gx, gy)]


def bordas(imagem: Imagem, operador: str = "sobel", limiar: float | None = None) -> Imagem:
    """Magnitude limitada a 0..255; com `limiar`, devolve mapa binário 0/255."""
    mag = magnitude(imagem, operador)
    if limiar is None:
        return limitar(mag)
    return [[255 if v >= limiar else 0 for v in linha] for linha in mag]
