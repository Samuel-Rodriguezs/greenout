"""Troco mínimo de moedas (programação dinâmica)."""


def troco_minimo(moedas: list[int], valor: int) -> int:
    """Menor quantidade de moedas que soma `valor`; -1 se for impossível."""
    if valor < 0:
        raise ValueError("valor não pode ser negativo")
    if any(m <= 0 for m in moedas):
        raise ValueError("moedas devem ser positivas")
    inf = valor + 1
    minimo = [0] + [inf] * valor
    for v in range(1, valor + 1):
        for m in moedas:
            if m <= v and minimo[v - m] + 1 < minimo[v]:
                minimo[v] = minimo[v - m] + 1
    return minimo[valor] if minimo[valor] != inf else -1
