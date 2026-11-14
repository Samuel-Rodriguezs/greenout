"""Codificação delta (DPCM e delta 1 bit) e compressão μ-law."""
from __future__ import annotations

import math

MU = 255.0


def delta_codificar(x: list[int]) -> list[int]:
    """DPCM: primeira amostra seguida das diferenças consecutivas."""
    if not x:
        return []
    return [x[0]] + [x[i] - x[i - 1] for i in range(1, len(x))]


def delta_decodificar(d: list[int]) -> list[int]:
    saida: list[int] = []
    acc = 0
    for v in d:
        acc += v
        saida.append(acc)
    return saida


def delta_1bit_codificar(x: list[float], passo: float) -> list[int]:
    """Modulação delta: 1 se o sinal está acima da estimativa, senão 0."""
    if passo <= 0:
        raise ValueError("passo deve ser positivo")
    bits = []
    est = 0.0
    for v in x:
        b = 1 if v > est else 0
        bits.append(b)
        est += passo if b else -passo
    return bits


def delta_1bit_decodificar(bits: list[int], passo: float) -> list[float]:
    """Reconstrução em escada; a saída corresponde à estimativa após cada bit."""
    if passo <= 0:
        raise ValueError("passo deve ser positivo")
    saida = []
    est = 0.0
    for b in bits:
        est += passo if b else -passo
        saida.append(est)
    return saida


def mulaw_comprimir(x: float, mu: float = MU) -> float:
    """F(x) = sgn(x) ln(1 + mu|x|) / ln(1 + mu), para x em [-1, 1]."""
    if not -1.0 <= x <= 1.0:
        raise ValueError("x deve estar em [-1, 1]")
    return math.copysign(math.log1p(mu * abs(x)) / math.log1p(mu), x)


def mulaw_expandir(y: float, mu: float = MU) -> float:
    """Inversa de mulaw_comprimir."""
    if not -1.0 <= y <= 1.0:
        raise ValueError("y deve estar em [-1, 1]")
    return math.copysign(((1 + mu) ** abs(y) - 1) / mu, y)


def mulaw_codificar(x: list[float], bits: int = 8) -> list[int]:
    """Comprime e quantiza em `bits` bits (índices 0..2^bits-1)."""
    if bits < 1:
        raise ValueError("bits deve ser >= 1")
    niveis = 2 ** bits
    saida = []
    for v in x:
        y = mulaw_comprimir(max(-1.0, min(1.0, v)))
        saida.append(min(niveis - 1, int((y + 1) / 2 * niveis)))
    return saida


def mulaw_decodificar(codigos: list[int], bits: int = 8) -> list[float]:
    """Reconstrói no centro de cada intervalo e expande."""
    niveis = 2 ** bits
    saida = []
    for c in codigos:
        if not 0 <= c < niveis:
            raise ValueError("código fora da faixa")
        saida.append(mulaw_expandir((c + 0.5) / niveis * 2 - 1))
    return saida
