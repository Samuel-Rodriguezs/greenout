"""Valores monetários fictícios com distribuição log-normal, em centavos (inteiros)."""
from __future__ import annotations

import math
import random
from decimal import Decimal


def parametros_por_mediana(mediana: float, sigma: float) -> tuple[float, float]:
    """(mu, sigma) da log-normal cuja mediana é `mediana` (mediana = exp(mu))."""
    if mediana <= 0 or sigma <= 0:
        raise ValueError("mediana e sigma devem ser positivos")
    return math.log(mediana), sigma


def gerar_centavos(
    rng: random.Random,
    mediana: float = 100.0,
    sigma: float = 0.8,
    minimo: int = 1,
    maximo: int | None = None,
) -> int:
    """Valor em centavos; `mediana` em reais. Truncado em [minimo, maximo] (nova tentativa)."""
    mu, s = parametros_por_mediana(mediana, sigma)
    if maximo is not None and maximo < minimo:
        raise ValueError("máximo menor que o mínimo")
    for _ in range(10_000):
        v = round(rng.lognormvariate(mu, s) * 100)
        if v >= minimo and (maximo is None or v <= maximo):
            return v
    raise RuntimeError("intervalo improvável para os parâmetros dados")


def gerar_lote(rng: random.Random, n: int, **kwargs) -> list[int]:
    return [gerar_centavos(rng, **kwargs) for _ in range(n)]


def formatar_brl(centavos: int) -> str:
    """Ex.: 123456 -> 'R$ 1.234,56'."""
    sinal = "-" if centavos < 0 else ""
    c = abs(centavos)
    inteiro, frac = divmod(c, 100)
    milhares = f"{inteiro:,}".replace(",", ".")
    return f"{sinal}R$ {milhares},{frac:02d}"


def para_decimal(centavos: int) -> Decimal:
    return Decimal(centavos) / Decimal(100)
