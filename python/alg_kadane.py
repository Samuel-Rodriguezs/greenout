"""Soma máxima de subarray contíguo (algoritmo de Kadane)."""


def soma_maxima_subarray(numeros: list[int]) -> int:
    """Maior soma de um trecho contíguo não vazio."""
    if not numeros:
        raise ValueError("a lista não pode ser vazia")
    melhor = atual = numeros[0]
    for n in numeros[1:]:
        atual = max(n, atual + n)
        melhor = max(melhor, atual)
    return melhor
