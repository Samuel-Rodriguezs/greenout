"""Permutações e subconjuntos por backtracking (sem usar itertools)."""


def permutacoes(itens: list) -> list[list]:
    """Todas as permutações de `itens`, em ordem lexicográfica de posição."""
    resultado: list[list] = []

    def gerar(atual: list, restantes: list) -> None:
        if not restantes:
            resultado.append(atual)
            return
        for i in range(len(restantes)):
            gerar(atual + [restantes[i]], restantes[:i] + restantes[i + 1:])

    gerar([], list(itens))
    return resultado


def subconjuntos(itens: list) -> list[list]:
    """Todos os subconjuntos (conjunto das partes), preservando a ordem dos itens."""
    resultado: list[list] = [[]]
    for item in itens:
        resultado += [s + [item] for s in resultado]
    return resultado
