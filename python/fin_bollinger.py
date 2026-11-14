"""Bandas de Bollinger e indicador %B."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Bandas:
    media: list[float | None]
    superior: list[float | None]
    inferior: list[float | None]


def bollinger(precos: list[float], n: int = 20, k: float = 2.0) -> Bandas:
    """Média móvel de n períodos +/- k desvios-padrão populacionais."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    m: list[float | None] = [None] * len(precos)
    sup: list[float | None] = [None] * len(precos)
    inf: list[float | None] = [None] * len(precos)
    for i in range(n - 1, len(precos)):
        janela = precos[i - n + 1 : i + 1]
        media = sum(janela) / n
        dp = math.sqrt(sum((x - media) ** 2 for x in janela) / n)
        m[i], sup[i], inf[i] = media, media + k * dp, media - k * dp
    return Bandas(m, sup, inf)


def percentual_b(preco: float, superior: float, inferior: float) -> float:
    """Posição do preço dentro das bandas: 0 = inferior, 1 = superior."""
    if superior == inferior:
        return 0.5
    return (preco - inferior) / (superior - inferior)
