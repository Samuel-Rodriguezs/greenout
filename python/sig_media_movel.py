"""Média móvel (simples e exponencial) e mediana móvel."""
from __future__ import annotations

from collections import deque


def media_movel(x: list[float], janela: int) -> list[float]:
    """Média dos últimos `janela` valores; no início usa o que houver."""
    if janela < 1:
        raise ValueError("janela deve ser >= 1")
    saida: list[float] = []
    buf: deque[float] = deque()
    soma = 0.0
    for v in x:
        buf.append(v)
        soma += v
        if len(buf) > janela:
            soma -= buf.popleft()
        saida.append(soma / len(buf))
    return saida


def media_exponencial(x: list[float], alfa: float) -> list[float]:
    """y[n] = alfa x[n] + (1-alfa) y[n-1]; y[0] = x[0]."""
    if not 0 < alfa <= 1:
        raise ValueError("alfa deve estar em (0, 1]")
    saida: list[float] = []
    for v in x:
        saida.append(v if not saida else alfa * v + (1 - alfa) * saida[-1])
    return saida


def mediana_movel(x: list[float], janela: int) -> list[float]:
    """Mediana centrada de janela ímpar; nas bordas a janela é truncada."""
    if janela < 1 or janela % 2 == 0:
        raise ValueError("janela deve ser ímpar e positiva")
    r = janela // 2
    saida: list[float] = []
    for i in range(len(x)):
        trecho = sorted(x[max(0, i - r): i + r + 1])
        m = len(trecho)
        saida.append(trecho[m // 2] if m % 2 else (trecho[m // 2 - 1] + trecho[m // 2]) / 2)
    return saida
