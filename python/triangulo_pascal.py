"""Triângulo de Pascal."""


def triangulo_pascal(linhas: int) -> list[list[int]]:
    """Gera as primeiras `linhas` linhas do triângulo; lista vazia para 0."""
    if linhas < 0:
        raise ValueError("número de linhas deve ser não negativo")
    triangulo: list[list[int]] = []
    for i in range(linhas):
        if i == 0:
            triangulo.append([1])
        else:
            anterior = triangulo[-1]
            triangulo.append([1] + [anterior[j] + anterior[j + 1] for j in range(i - 1)] + [1])
    return triangulo
