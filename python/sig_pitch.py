"""Detecção de frequência fundamental por autocorrelação."""
from __future__ import annotations

from sig_convolucao import autocorrelacao


def frequencia_fundamental(x: list[float], taxa: float, fmin: float = 50.0,
                           fmax: float = 1000.0, limiar: float = 0.3) -> float | None:
    """Estima f0 (Hz) ou None se o sinal não for periódico o bastante.

    Procura o maior pico da autocorrelação normalizada entre os lags
    correspondentes a fmax e fmin, com interpolação parabólica.
    """
    if taxa <= 0 or fmin <= 0 or fmax <= fmin:
        raise ValueError("parâmetros inválidos")
    n = len(x)
    lag_min = max(1, int(taxa / fmax))
    lag_max = min(n - 2, int(taxa / fmin))
    if lag_max <= lag_min:
        return None
    media = sum(x) / n
    centrado = [v - media for v in x]
    r = autocorrelacao(centrado)
    if r[0] <= 0:
        return None
    # normaliza pela sobreposição para não favorecer lags curtos
    rn = [r[k] / r[0] * n / (n - k) for k in range(n)]
    teto = max(rn[lag_min:lag_max + 1])
    if teto < limiar:
        return None
    # primeiro máximo local próximo do teto: evita escolher múltiplos do período
    melhor = next(
        (k for k in range(lag_min, lag_max + 1)
         if rn[k] >= 0.9 * teto and rn[k] >= rn[k - 1] and rn[k] >= rn[k + 1]),
        None,
    )
    if melhor is None:
        return None
    a, b, c = rn[melhor - 1], rn[melhor], rn[melhor + 1]
    den = a - 2 * b + c
    delta = 0.5 * (a - c) / den if den != 0 else 0.0
    return taxa / (melhor + delta)


def periodo_em_amostras(x: list[float], taxa: float, **kw) -> float | None:
    """Período estimado em amostras (inverso de f0 vezes a taxa)."""
    f0 = frequencia_fundamental(x, taxa, **kw)
    return None if f0 is None else taxa / f0
