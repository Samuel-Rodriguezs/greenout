"""Yahtzee Kata: pontuação por categoria para cinco dados."""
from __future__ import annotations

from collections import Counter

CATEGORIAS = (
    "chance", "yahtzee", "uns", "dois", "tres", "quatros", "cincos", "seis",
    "par", "dois_pares", "trinca", "quadra", "sequencia_pequena",
    "sequencia_grande", "full_house",
)
_NUMEROS = {"uns": 1, "dois": 2, "tres": 3, "quatros": 4, "cincos": 5, "seis": 6}


def pontuar(dados: list[int], categoria: str) -> int:
    if len(dados) != 5 or any(not 1 <= d <= 6 for d in dados):
        raise ValueError("são necessários 5 dados com valores de 1 a 6")
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria desconhecida: {categoria}")
    cont = Counter(dados)
    if categoria == "chance":
        return sum(dados)
    if categoria == "yahtzee":
        return 50 if len(cont) == 1 else 0
    if categoria in _NUMEROS:
        n = _NUMEROS[categoria]
        return n * cont[n]
    if categoria == "par":
        pares = [v for v, c in cont.items() if c >= 2]
        return 2 * max(pares) if pares else 0
    if categoria == "dois_pares":
        pares = sorted((v for v, c in cont.items() if c >= 2), reverse=True)
        return 2 * (pares[0] + pares[1]) if len(pares) >= 2 else 0
    if categoria == "trinca":
        trincas = [v for v, c in cont.items() if c >= 3]
        return 3 * max(trincas) if trincas else 0
    if categoria == "quadra":
        quadras = [v for v, c in cont.items() if c >= 4]
        return 4 * max(quadras) if quadras else 0
    if categoria == "sequencia_pequena":
        return 15 if sorted(dados) == [1, 2, 3, 4, 5] else 0
    if categoria == "sequencia_grande":
        return 20 if sorted(dados) == [2, 3, 4, 5, 6] else 0
    # full_house: exatamente uma trinca e um par
    if sorted(cont.values()) == [2, 3]:
        return sum(dados)
    return 0
