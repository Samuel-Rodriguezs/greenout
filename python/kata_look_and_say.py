"""Conway Sequence (look-and-say) Kata."""
from __future__ import annotations

from collections.abc import Iterator
from itertools import groupby


def proximo(termo: str) -> str:
    """Lê o termo em voz alta: '1211' -> 'um 1, um 2, dois 1' -> '111221'."""
    if not termo or not termo.isdigit():
        raise ValueError("termo deve ser uma string de dígitos não vazia")
    return "".join(f"{sum(1 for _ in g)}{d}" for d, g in groupby(termo))


def sequencia(semente: str = "1") -> Iterator[str]:
    termo = semente
    while True:
        yield termo
        termo = proximo(termo)


def termo(n: int, semente: str = "1") -> str:
    """n-ésimo termo (base 1)."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    atual = semente
    for _ in range(n - 1):
        atual = proximo(atual)
    return atual


def decodificar(texto: str) -> str:
    """Inverso de proximo (um dos possíveis pais)."""
    if len(texto) % 2 or not texto.isdigit():
        raise ValueError("texto inválido")
    return "".join(texto[i + 1] * int(texto[i]) for i in range(0, len(texto), 2))
