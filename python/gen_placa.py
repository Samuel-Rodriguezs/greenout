"""Placas Mercosul (e antigas) fictícias."""
from __future__ import annotations

import random
import string


def gerar_placa_mercosul(rng: random.Random) -> str:
    """Formato LLLNLNN (ex.: ABC1D23)."""
    letras = string.ascii_uppercase
    p = (
        "".join(rng.choice(letras) for _ in range(3))
        + str(rng.randint(0, 9))
        + rng.choice(letras)
        + f"{rng.randint(0, 99):02d}"
    )
    return p


def gerar_placa_antiga(rng: random.Random, formatada: bool = True) -> str:
    """Formato LLL-NNNN."""
    letras = "".join(rng.choice(string.ascii_uppercase) for _ in range(3))
    num = f"{rng.randint(0, 9999):04d}"
    return f"{letras}-{num}" if formatada else letras + num


def antiga_para_mercosul(placa: str) -> str:
    """Conversão padrão: o 2º dígito numérico vira a letra correspondente (0=A ... 9=J)."""
    p = placa.replace("-", "").upper()
    if len(p) != 7 or not p[:3].isalpha() or not p[3:].isdigit():
        raise ValueError(f"placa antiga inválida: {placa!r}")
    return p[:4] + string.ascii_uppercase[int(p[4])] + p[5:]


def gerar_lote(rng: random.Random, n: int, proporcao_mercosul: float = 0.7) -> list[str]:
    """Placas distintas, misturando os dois modelos."""
    if not 0.0 <= proporcao_mercosul <= 1.0:
        raise ValueError("proporção deve estar em [0, 1]")
    vistos: set[str] = set()
    saida: list[str] = []
    while len(saida) < n:
        if rng.random() < proporcao_mercosul:
            p = gerar_placa_mercosul(rng)
        else:
            p = gerar_placa_antiga(rng)
        chave = p.replace("-", "")
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(p)
    return saida
