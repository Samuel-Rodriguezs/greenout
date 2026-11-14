"""Problema da mochila 0/1 resolvido com programação dinâmica."""


def mochila(pesos: list[int], valores: list[int], capacidade: int) -> int:
    """Retorna o maior valor possível sem exceder a capacidade."""
    if len(pesos) != len(valores):
        raise ValueError("pesos e valores devem ter o mesmo tamanho")
    if capacidade < 0:
        raise ValueError("capacidade não pode ser negativa")
    melhor = [0] * (capacidade + 1)
    for peso, valor in zip(pesos, valores):
        for c in range(capacidade, peso - 1, -1):
            melhor[c] = max(melhor[c], melhor[c - peso] + valor)
    return melhor[capacidade]
