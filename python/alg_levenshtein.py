"""Distância de edição (Levenshtein) entre duas strings."""


def distancia_edicao(a: str, b: str) -> int:
    """Número mínimo de inserções, remoções e substituições para transformar a em b."""
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        atual = [i]
        for j, cb in enumerate(b, start=1):
            custo = 0 if ca == cb else 1
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + custo))
        anterior = atual
    return anterior[-1]
