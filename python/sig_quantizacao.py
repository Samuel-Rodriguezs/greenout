"""Quantização uniforme, erro de quantização e SNR."""
from __future__ import annotations

import math


def quantizar(x: list[float], bits: int, vmax: float = 1.0) -> list[float]:
    """Quantizador uniforme mid-rise de `bits` bits no intervalo [-vmax, vmax]."""
    if bits < 1:
        raise ValueError("bits deve ser >= 1")
    if vmax <= 0:
        raise ValueError("vmax deve ser positivo")
    niveis = 2 ** bits
    passo = 2 * vmax / niveis
    saida = []
    for v in x:
        v = max(-vmax, min(vmax, v))
        idx = min(niveis - 1, int((v + vmax) / passo))
        saida.append(-vmax + (idx + 0.5) * passo)
    return saida


def indices(x: list[float], bits: int, vmax: float = 1.0) -> list[int]:
    """Índices inteiros (0..2^bits-1) dos níveis do quantizador."""
    if bits < 1 or vmax <= 0:
        raise ValueError("parâmetros inválidos")
    niveis = 2 ** bits
    passo = 2 * vmax / niveis
    return [min(niveis - 1, int((max(-vmax, min(vmax, v)) + vmax) / passo)) for v in x]


def erro_de_quantizacao(original: list[float], quantizado: list[float]) -> list[float]:
    if len(original) != len(quantizado):
        raise ValueError("tamanhos diferentes")
    return [q - o for o, q in zip(original, quantizado)]


def snr_db(sinal: list[float], aproximado: list[float]) -> float:
    """SNR em dB entre sinal e sua aproximação; infinito se não houver erro."""
    erro = erro_de_quantizacao(sinal, aproximado)
    p_sinal = sum(v * v for v in sinal)
    p_erro = sum(e * e for e in erro)
    if p_erro == 0:
        return math.inf
    if p_sinal == 0:
        return -math.inf
    return 10 * math.log10(p_sinal / p_erro)


def snr_teorico(bits: int) -> float:
    """SNR ideal (dB) para um seno de escala plena: 6,02 N + 1,76."""
    return 6.02 * bits + 1.76
