"""Amostragem de funções contínuas e reamostragem linear."""
from __future__ import annotations

from typing import Callable


def amostrar(f: Callable[[float], float], taxa: float, duracao: float) -> list[float]:
    """Amostra f(t) em t = k/taxa para 0 <= t < duracao."""
    if taxa <= 0 or duracao < 0:
        raise ValueError("taxa deve ser positiva e duração não negativa")
    n = round(duracao * taxa)
    return [f(k / taxa) for k in range(n)]


def interpolar(x: list[float], posicao: float) -> float:
    """Valor interpolado linearmente na posição fracionária (fixa nas bordas)."""
    if not x:
        raise ValueError("sinal vazio")
    if posicao <= 0:
        return x[0]
    if posicao >= len(x) - 1:
        return x[-1]
    i = int(posicao)
    frac = posicao - i
    return x[i] * (1 - frac) + x[i + 1] * frac


def reamostrar(x: list[float], taxa_origem: float, taxa_destino: float) -> list[float]:
    """Reamostra por interpolação linear (sem filtro anti-aliasing)."""
    if taxa_origem <= 0 or taxa_destino <= 0:
        raise ValueError("taxas devem ser positivas")
    if not x:
        return []
    n = max(1, round(len(x) * taxa_destino / taxa_origem))
    passo = taxa_origem / taxa_destino
    return [interpolar(x, k * passo) for k in range(n)]


def decimar(x: list[float], fator: int) -> list[float]:
    """Mantém uma a cada `fator` amostras."""
    if fator < 1:
        raise ValueError("fator deve ser >= 1")
    return x[::fator]


def inserir_zeros(x: list[float], fator: int) -> list[float]:
    """Expansão: insere fator-1 zeros após cada amostra."""
    if fator < 1:
        raise ValueError("fator deve ser >= 1")
    saida: list[float] = []
    for v in x:
        saida.append(v)
        saida.extend([0.0] * (fator - 1))
    return saida


def nyquist(taxa: float) -> float:
    """Maior frequência representável sem aliasing."""
    return taxa / 2


def frequencia_aparente(freq: float, taxa: float) -> float:
    """Frequência observada (0..taxa/2) após amostragem, considerando aliasing."""
    if taxa <= 0:
        raise ValueError("taxa deve ser positiva")
    r = abs(freq) % taxa
    return taxa - r if r > taxa / 2 else r
