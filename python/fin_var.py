"""Value at Risk e Expected Shortfall: histórico e paramétrico (normal)."""
from __future__ import annotations

from statistics import NormalDist


def quantil(valores: list[float], q: float) -> float:
    """Quantil com interpolação linear entre estatísticas de ordem."""
    if not valores:
        raise ValueError("série vazia")
    if not 0 <= q <= 1:
        raise ValueError("q deve estar em [0, 1]")
    v = sorted(valores)
    pos = (len(v) - 1) * q
    i = int(pos)
    if i + 1 >= len(v):
        return v[-1]
    return v[i] + (pos - i) * (v[i + 1] - v[i])


def _validar_conf(confianca: float) -> None:
    if not 0 < confianca < 1:
        raise ValueError("confiança deve estar entre 0 e 1")


def var_historico(retornos: list[float], confianca: float = 0.95) -> float:
    """Perda (positiva) não excedida com a confiança dada."""
    _validar_conf(confianca)
    return -quantil(retornos, 1 - confianca)


def cvar_historico(retornos: list[float], confianca: float = 0.95) -> float:
    """Média das perdas na cauda além do VaR."""
    _validar_conf(confianca)
    corte = quantil(retornos, 1 - confianca)
    cauda = [r for r in retornos if r <= corte]
    return -sum(cauda) / len(cauda)


def var_parametrico(
    media: float, desvio: float, confianca: float = 0.95
) -> float:
    """VaR assumindo retornos normais: -(mu + z*sigma)."""
    _validar_conf(confianca)
    if desvio < 0:
        raise ValueError("desvio não pode ser negativo")
    z = NormalDist().inv_cdf(1 - confianca)
    return -(media + z * desvio)
