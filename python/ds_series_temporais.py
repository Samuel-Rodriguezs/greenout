"""Séries temporais: diferenciação, sazonalidade simples, tendência e autocorrelação."""
from __future__ import annotations

from typing import Sequence


def diferenciar(serie: Sequence[float], lag: int = 1, ordem: int = 1) -> list[float]:
    if lag <= 0 or ordem <= 0:
        raise ValueError("lag e ordem devem ser positivos")
    atual = list(serie)
    for _ in range(ordem):
        if len(atual) <= lag:
            raise ValueError("série curta demais para a diferenciação")
        atual = [atual[i] - atual[i - lag] for i in range(lag, len(atual))]
    return atual


def integrar(diffs: Sequence[float], inicial: float) -> list[float]:
    """Inverso da diferenciação de lag 1 (devolve a série com o valor inicial)."""
    saida = [float(inicial)]
    for d in diffs:
        saida.append(saida[-1] + d)
    return saida


def indices_sazonais(serie: Sequence[float], periodo: int) -> list[float]:
    """Média de cada posição do ciclo dividida pela média global (modelo multiplicativo)."""
    if periodo <= 0:
        raise ValueError("período deve ser positivo")
    if len(serie) < periodo:
        raise ValueError("série menor que um período")
    geral = sum(serie) / len(serie)
    if geral == 0:
        raise ValueError("média global nula")
    indices = []
    for p in range(periodo):
        vals = serie[p::periodo]
        indices.append((sum(vals) / len(vals)) / geral)
    return indices


def dessazonalizar(serie: Sequence[float], periodo: int) -> list[float]:
    ind = indices_sazonais(serie, periodo)
    if any(i == 0 for i in ind):
        raise ValueError("índice sazonal nulo")
    return [x / ind[i % periodo] for i, x in enumerate(serie)]


def tendencia_linear(serie: Sequence[float]) -> tuple[float, float]:
    """(intercepto, inclinação) da reta ajustada contra t = 0..n-1."""
    n = len(serie)
    if n < 2:
        raise ValueError("são necessárias ao menos 2 observações")
    mt = (n - 1) / 2
    my = sum(serie) / n
    sxx = sum((t - mt) ** 2 for t in range(n))
    sxy = sum((t - mt) * (y - my) for t, y in enumerate(serie))
    b = sxy / sxx
    return my - b * mt, b


def autocorrelacao(serie: Sequence[float], lag: int) -> float:
    n = len(serie)
    if not 0 <= lag < n:
        raise ValueError("lag fora do intervalo")
    m = sum(serie) / n
    den = sum((x - m) ** 2 for x in serie)
    if den == 0:
        raise ValueError("série constante")
    num = sum((serie[t] - m) * (serie[t - lag] - m) for t in range(lag, n))
    return num / den
