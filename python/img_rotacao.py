"""Rotação em múltiplos de 90 graus, espelhamento e transposição de matrizes."""

from typing import TypeVar

T = TypeVar("T")
Matriz = list[list[T]]


def transpor(imagem: Matriz) -> Matriz:
    return [list(col) for col in zip(*imagem)]


def espelhar_horizontal(imagem: Matriz) -> Matriz:
    """Troca esquerda por direita."""
    return [linha[::-1] for linha in imagem]


def espelhar_vertical(imagem: Matriz) -> Matriz:
    """Troca topo por base."""
    return [list(linha) for linha in imagem[::-1]]


def rotacionar_90(imagem: Matriz, vezes: int = 1) -> Matriz:
    """Gira `vezes` quartos de volta no sentido horário (negativo = anti-horário)."""
    vezes %= 4
    if vezes == 0:
        return [list(linha) for linha in imagem]
    if vezes == 1:
        return espelhar_horizontal(transpor(imagem))
    if vezes == 2:
        return rotacionar_180(imagem)
    return espelhar_vertical(transpor(imagem))


def rotacionar_180(imagem: Matriz) -> Matriz:
    return [linha[::-1] for linha in imagem[::-1]]
