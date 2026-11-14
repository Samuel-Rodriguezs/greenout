"""Medidas de similaridade entre textos: cosseno, Jaccard, Dice e Levenshtein normalizado."""
import math
from collections import Counter


def cosseno(a: list[str], b: list[str]) -> float:
    ca, cb = Counter(a), Counter(b)
    dot = sum(ca[t] * cb[t] for t in ca.keys() & cb.keys())
    na = math.sqrt(sum(v * v for v in ca.values()))
    nb = math.sqrt(sum(v * v for v in cb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def jaccard(a: set | list, b: set | list) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def dice(a: set | list, b: set | list) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return 2 * len(sa & sb) / (len(sa) + len(sb))


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            atual.append(min(anterior[j] + 1, atual[j - 1] + 1, anterior[j - 1] + (ca != cb)))
        anterior = atual
    return anterior[-1]


def levenshtein_normalizada(a: str, b: str) -> float:
    """Similaridade em [0, 1]: 1 - distância / maior comprimento."""
    if not a and not b:
        return 1.0
    return 1 - levenshtein(a, b) / max(len(a), len(b))
