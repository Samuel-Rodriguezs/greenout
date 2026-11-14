"""Faixa verdadeira (True Range) e ATR com suavização de Wilder."""
from __future__ import annotations


def true_range(
    maximas: list[float], minimas: list[float], fechamentos: list[float]
) -> list[float]:
    if not (len(maximas) == len(minimas) == len(fechamentos)):
        raise ValueError("séries com tamanhos diferentes")
    tr: list[float] = []
    for i, (h, low) in enumerate(zip(maximas, minimas)):
        if i == 0:
            tr.append(h - low)
        else:
            anterior = fechamentos[i - 1]
            tr.append(max(h - low, abs(h - anterior), abs(low - anterior)))
    return tr


def atr(
    maximas: list[float],
    minimas: list[float],
    fechamentos: list[float],
    n: int = 14,
) -> list[float | None]:
    """ATR: média dos n primeiros TR e depois (ATR*(n-1) + TR)/n."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    tr = true_range(maximas, minimas, fechamentos)
    saida: list[float | None] = [None] * len(tr)
    if len(tr) < n:
        return saida
    atual = sum(tr[:n]) / n
    saida[n - 1] = atual
    for i in range(n, len(tr)):
        atual = (atual * (n - 1) + tr[i]) / n
        saida[i] = atual
    return saida
