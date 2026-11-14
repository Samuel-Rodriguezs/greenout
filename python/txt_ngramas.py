"""N-gramas de palavras e de caracteres."""
from collections import Counter
from typing import Sequence, TypeVar

T = TypeVar("T")


def ngramas(itens: Sequence[T], n: int) -> list[tuple[T, ...]]:
    if n < 1:
        raise ValueError("n deve ser >= 1")
    return [tuple(itens[i:i + n]) for i in range(len(itens) - n + 1)]


def ngramas_caracteres(texto: str, n: int) -> list[str]:
    return ["".join(g) for g in ngramas(texto, n)]


def contar_ngramas(itens: Sequence[T], n: int) -> Counter:
    return Counter(ngramas(itens, n))
