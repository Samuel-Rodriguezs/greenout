"""Oscilador estocástico (%K e %D)."""
from __future__ import annotations


def estocastico(
    maximas: list[float],
    minimas: list[float],
    fechamentos: list[float],
    n: int = 14,
    suavizacao: int = 3,
) -> tuple[list[float | None], list[float | None]]:
    """Devolve (%K, %D); %D é a média simples de %K em `suavizacao` períodos."""
    if not (len(maximas) == len(minimas) == len(fechamentos)):
        raise ValueError("séries com tamanhos diferentes")
    if n <= 0 or suavizacao <= 0:
        raise ValueError("períodos devem ser positivos")
    total = len(fechamentos)
    k: list[float | None] = [None] * total
    for i in range(n - 1, total):
        hh = max(maximas[i - n + 1 : i + 1])
        ll = min(minimas[i - n + 1 : i + 1])
        k[i] = 50.0 if hh == ll else (fechamentos[i] - ll) / (hh - ll) * 100
    d: list[float | None] = [None] * total
    for i in range(n - 1 + suavizacao - 1, total):
        janela = k[i - suavizacao + 1 : i + 1]
        d[i] = sum(janela) / suavizacao  # type: ignore[arg-type]
    return k, d
