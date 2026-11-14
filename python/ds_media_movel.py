"""Médias móveis (simples e ponderada) e suavização exponencial."""
from __future__ import annotations

from typing import Sequence


def media_movel(dados: Sequence[float], janela: int) -> list[float]:
    """Média móvel simples; só janelas completas (len = n - janela + 1)."""
    if janela <= 0:
        raise ValueError("janela deve ser positiva")
    if janela > len(dados):
        raise ValueError("janela maior que a série")
    soma = sum(dados[:janela])
    saida = [soma / janela]
    for i in range(janela, len(dados)):
        soma += dados[i] - dados[i - janela]
        saida.append(soma / janela)
    return saida


def media_movel_ponderada(dados: Sequence[float], pesos: Sequence[float]) -> list[float]:
    """Pesos aplicados do mais antigo ao mais recente da janela."""
    k = len(pesos)
    if k == 0 or sum(pesos) == 0:
        raise ValueError("pesos inválidos")
    if k > len(dados):
        raise ValueError("janela maior que a série")
    total = sum(pesos)
    return [sum(p * x for p, x in zip(pesos, dados[i : i + k])) / total for i in range(len(dados) - k + 1)]


def suavizacao_exponencial(dados: Sequence[float], alfa: float) -> list[float]:
    """s0 = x0; st = alfa*xt + (1-alfa)*s(t-1)."""
    if not 0 < alfa <= 1:
        raise ValueError("alfa deve estar em (0, 1]")
    if not dados:
        raise ValueError("dados vazios")
    s = [float(dados[0])]
    for x in dados[1:]:
        s.append(alfa * x + (1 - alfa) * s[-1])
    return s


def holt(dados: Sequence[float], alfa: float, beta: float, horizonte: int = 1) -> list[float]:
    """Suavização exponencial dupla (tendência linear); devolve previsões futuras."""
    if len(dados) < 2:
        raise ValueError("são necessários ao menos 2 pontos")
    nivel, tend = float(dados[0]), float(dados[1] - dados[0])
    for x in dados[1:]:
        anterior = nivel
        nivel = alfa * x + (1 - alfa) * (nivel + tend)
        tend = beta * (nivel - anterior) + (1 - beta) * tend
    return [nivel + h * tend for h in range(1, horizonte + 1)]
