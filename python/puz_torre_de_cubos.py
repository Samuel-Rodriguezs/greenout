"""Torre de cubos (Instant Insanity): empilhar n cubos coloridos de modo que cada lado mostre todas as cores."""
from __future__ import annotations

from typing import Optional

# Cubo: cores das faces (topo, base, frente, trás, esquerda, direita).
Cubo = tuple[str, str, str, str, str, str]


def _girar_vertical(c: Cubo) -> Cubo:
    """Gira 90 graus em torno do eixo vertical (topo/base fixos)."""
    t, b, f, k, e, d = c
    return (t, b, d, e, f, k)


def _tombar(c: Cubo) -> Cubo:
    """Gira 90 graus em torno do eixo esquerda-direita."""
    t, b, f, k, e, d = c
    return (k, f, t, b, e, d)


def _tombar_lado(c: Cubo) -> Cubo:
    """Gira 90 graus em torno do eixo frente-trás."""
    t, b, f, k, e, d = c
    return (e, d, f, k, b, t)


def orientacoes(c: Cubo) -> list[Cubo]:
    """As 24 orientações distintas (as que repetem aparência de cores não são removidas)."""
    vistas: set[Cubo] = set()
    saida: list[Cubo] = []
    pilha = [c]
    while pilha:
        x = pilha.pop()
        if x in vistas:
            continue
        vistas.add(x)
        saida.append(x)
        pilha += [_girar_vertical(x), _tombar(x), _tombar_lado(x)]
    return saida


def resolver(cubos: list[Cubo]) -> Optional[list[Cubo]]:
    """Orientação de cada cubo (de baixo para cima) ou None.

    Exige que, nos quatro lados (frente, trás, esquerda, direita), as n cores sejam todas distintas;
    portanto cada cubo precisa ter n cores diferentes disponíveis.
    """
    n = len(cubos)
    if n == 0:
        return []
    cores = {x for c in cubos for x in c}
    if len(cores) < n:
        return None
    opcoes = [orientacoes(c) for c in cubos]
    escolha: list[Cubo] = []
    usados = [set() for _ in range(4)]  # frente, trás, esquerda, direita

    def busca(i: int) -> bool:
        if i == n:
            return True
        for o in opcoes[i]:
            lados = o[2:]
            if all(lados[k] not in usados[k] for k in range(4)):
                for k in range(4):
                    usados[k].add(lados[k])
                escolha.append(o)
                if busca(i + 1):
                    return True
                escolha.pop()
                for k in range(4):
                    usados[k].discard(lados[k])
        return False

    return list(escolha) if busca(0) else None


def verificar(torre: list[Cubo]) -> bool:
    n = len(torre)
    return all(len({c[k] for c in torre}) == n for k in range(2, 6))


def mesmo_cubo(a: Cubo, b: Cubo) -> bool:
    """Verdadeiro se b é uma orientação de a."""
    return b in orientacoes(a)


# Quatro cubos com cores R, G, B, W (embaralhados a partir de uma torre solucionável)
CLASSICO: list[Cubo] = [
    ("B", "G", "W", "B", "G", "R"),
    ("B", "G", "R", "W", "W", "R"),
    ("G", "R", "B", "B", "W", "B"),
    ("R", "W", "B", "G", "W", "R"),
]
