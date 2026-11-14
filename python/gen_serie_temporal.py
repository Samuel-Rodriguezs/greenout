"""Séries temporais sintéticas: tendência linear + sazonalidade senoidal + ruído gaussiano."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ParametrosSerie:
    nivel: float = 100.0
    tendencia: float = 0.5  # incremento por passo
    amplitude: float = 10.0
    periodo: int = 7  # passos por ciclo sazonal
    fase: float = 0.0
    ruido: float = 2.0  # desvio-padrão


def componentes(p: ParametrosSerie, n: int) -> tuple[list[float], list[float]]:
    """(tendência, sazonalidade) determinísticas para n passos."""
    if p.periodo <= 0:
        raise ValueError("período deve ser positivo")
    if p.ruido < 0:
        raise ValueError("ruído não pode ser negativo")
    tend = [p.nivel + p.tendencia * t for t in range(n)]
    saz = [p.amplitude * math.sin(2 * math.pi * t / p.periodo + p.fase) for t in range(n)]
    return tend, saz


def gerar_serie(rng: random.Random, p: ParametrosSerie, n: int) -> list[float]:
    tend, saz = componentes(p, n)
    return [tend[t] + saz[t] + rng.gauss(0.0, p.ruido) for t in range(n)]


def gerar_serie_datada(
    rng: random.Random, p: ParametrosSerie, inicio: date, n: int
) -> list[tuple[date, float]]:
    valores = gerar_serie(rng, p, n)
    return [(inicio + timedelta(days=i), v) for i, v in enumerate(valores)]


def media_movel(valores: list[float], janela: int) -> list[float]:
    """Média móvel simples (saída com len(valores) - janela + 1 pontos)."""
    if janela <= 0 or janela > len(valores):
        raise ValueError("janela inválida")
    soma = sum(valores[:janela])
    saida = [soma / janela]
    for i in range(janela, len(valores)):
        soma += valores[i] - valores[i - janela]
        saida.append(soma / janela)
    return saida
