"""Modulação AM e FM (banda base discreta) e demodulação por envelope/fase."""
from __future__ import annotations

import math


def modular_am(mensagem: list[float], fc: float, taxa: float, indice: float = 0.5) -> list[float]:
    """s[n] = (1 + m * msg[n]) cos(2π fc n / taxa); |msg| <= 1 recomendado."""
    _validar(fc, taxa)
    return [(1 + indice * m) * math.cos(2 * math.pi * fc * n / taxa) for n, m in enumerate(mensagem)]


def modular_fm(mensagem: list[float], fc: float, taxa: float, desvio: float) -> list[float]:
    """FM com desvio máximo de frequência `desvio` Hz para |msg| = 1."""
    _validar(fc, taxa)
    if desvio < 0:
        raise ValueError("desvio não pode ser negativo")
    fase = 0.0
    saida = []
    for n, m in enumerate(mensagem):
        saida.append(math.cos(2 * math.pi * fc * n / taxa + fase))
        fase += 2 * math.pi * desvio * m / taxa
    return saida


def _validar(fc: float, taxa: float) -> None:
    if taxa <= 0 or not 0 < fc < taxa / 2:
        raise ValueError("portadora deve estar entre 0 e taxa/2")


def demodular_am(sinal: list[float], janela: int) -> list[float]:
    """Envelope por retificação de onda completa e média móvel (reescalada por π/2)."""
    if janela < 1:
        raise ValueError("janela deve ser >= 1")
    ret = [abs(v) for v in sinal]
    saida = []
    soma = 0.0
    for i, v in enumerate(ret):
        soma += v
        if i >= janela:
            soma -= ret[i - janela]
        saida.append(soma / min(i + 1, janela) * math.pi / 2)
    return saida


def frequencia_instantanea(sinal: list[float], taxa: float) -> list[float]:
    """Frequência instantânea (Hz) de um cosseno de amplitude constante.

    Usa a identidade de três pontos cos(w) = (s[n+1] + s[n-1]) / (2 s[n]);
    onde s[n] é quase zero repete a estimativa anterior.
    """
    saida = []
    for n in range(1, len(sinal) - 1):
        if abs(sinal[n]) < 1e-6:
            saida.append(saida[-1] if saida else 0.0)
            continue
        c = (sinal[n + 1] + sinal[n - 1]) / (2 * sinal[n])
        c = max(-1.0, min(1.0, c))
        saida.append(math.acos(c) * taxa / (2 * math.pi))
    return saida
