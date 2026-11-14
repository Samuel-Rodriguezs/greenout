"""Matriz de posição (PFM/PWM) e conservação por coluna de um alinhamento."""

import math

BASES = "ACGT"


def _checar(alin: list[str]) -> None:
    if not alin or not alin[0] or any(len(s) != len(alin[0]) for s in alin):
        raise ValueError("alinhamento vazio ou com tamanhos diferentes")


def contagens(alin: list[str]) -> dict[str, list[int]]:
    """Contagem de cada base (ACGT) por coluna."""
    _checar(alin)
    return {b: [sum(s[i] == b for s in alin) for i in range(len(alin[0]))] for b in BASES}


def frequencias(alin: list[str]) -> dict[str, list[float]]:
    n = len(alin)
    return {b: [c / n for c in v] for b, v in contagens(alin).items()}


def pwm(alin: list[str], pseudo: float = 0.5, fundo: float = 0.25) -> dict[str, list[float]]:
    """Log2 da razão entre frequência suavizada e frequência de fundo."""
    n = len(alin)
    return {
        b: [math.log2((c + pseudo) / (n + 4 * pseudo) / fundo) for c in v]
        for b, v in contagens(alin).items()
    }


def informacao(alin: list[str]) -> list[float]:
    """Conteúdo de informação (bits) por coluna: 2 - entropia de Shannon."""
    f = frequencias(alin)
    res = []
    for i in range(len(alin[0])):
        h = -sum(f[b][i] * math.log2(f[b][i]) for b in BASES if f[b][i] > 0)
        res.append(2 - h)
    return res
