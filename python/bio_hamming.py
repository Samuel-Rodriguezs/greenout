"""Distância de Hamming entre sequências de mesmo tamanho."""


def distancia(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("sequências com tamanhos diferentes")
    return sum(x != y for x, y in zip(a, b))


def posicoes_diferentes(a: str, b: str) -> list[int]:
    """Índices (base 0) onde as sequências divergem."""
    if len(a) != len(b):
        raise ValueError("sequências com tamanhos diferentes")
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def proporcao(a: str, b: str) -> float:
    """Distância normalizada (p-distance)."""
    if not a and not b:
        return 0.0
    return distancia(a, b) / len(a)
