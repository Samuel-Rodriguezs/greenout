"""Estatística descritiva básica."""
from collections import Counter
from math import sqrt
from typing import List, Sequence


def _vazio(d: Sequence[float]) -> None:
    if not d:
        raise ValueError("dados vazios")


def media(d: Sequence[float]) -> float:
    _vazio(d)
    return sum(d) / len(d)


def mediana(d: Sequence[float]) -> float:
    _vazio(d)
    s = sorted(d)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def moda(d: Sequence[float]) -> List[float]:
    """Todos os valores mais frequentes, em ordem crescente."""
    _vazio(d)
    c = Counter(d)
    m = max(c.values())
    return sorted(k for k, v in c.items() if v == m)


def variancia(d: Sequence[float], amostral: bool = False) -> float:
    _vazio(d)
    if amostral and len(d) < 2:
        raise ValueError("variância amostral exige ao menos 2 valores")
    mu = media(d)
    return sum((x - mu) ** 2 for x in d) / (len(d) - (1 if amostral else 0))


def desvio_padrao(d: Sequence[float], amostral: bool = False) -> float:
    return sqrt(variancia(d, amostral))
