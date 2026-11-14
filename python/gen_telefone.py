"""Telefones celulares brasileiros fictícios com DDD válido."""
from __future__ import annotations

import random

DDDS_VALIDOS: tuple[int, ...] = (
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68,
    69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95,
    96, 97, 98, 99,
)


def gerar_celular(rng: random.Random, ddd: int | None = None) -> str:
    """Somente dígitos: DDD + 9 + 8 dígitos (11 dígitos)."""
    if ddd is None:
        ddd = rng.choice(DDDS_VALIDOS)
    elif ddd not in DDDS_VALIDOS:
        raise ValueError(f"DDD inválido: {ddd}")
    return f"{ddd}9{rng.randint(0, 99_999_999):08d}"


def formatar_celular(numero: str) -> str:
    if len(numero) != 11 or not numero.isdigit():
        raise ValueError("celular deve ter 11 dígitos")
    return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"


def eh_celular_valido(numero: str) -> bool:
    return (
        len(numero) == 11
        and numero.isdigit()
        and int(numero[:2]) in DDDS_VALIDOS
        and numero[2] == "9"
    )


def gerar_lote(rng: random.Random, n: int, unicos: bool = True) -> list[str]:
    saida: list[str] = []
    vistos: set[str] = set()
    while len(saida) < n:
        t = gerar_celular(rng)
        if unicos and t in vistos:
            continue
        vistos.add(t)
        saida.append(t)
    return saida
