"""Geração reprodutível de CPF e CNPJ fictícios com dígitos verificadores corretos."""
from __future__ import annotations

import random


def _dv_cpf(digitos: list[int]) -> int:
    peso = len(digitos) + 1
    soma = sum(d * (peso - i) for i, d in enumerate(digitos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def gerar_cpf(rng: random.Random, formatado: bool = False) -> str:
    """CPF válido, nunca com os 11 dígitos iguais."""
    while True:
        base = [rng.randint(0, 9) for _ in range(9)]
        if len(set(base)) > 1:
            break
    base.append(_dv_cpf(base))
    base.append(_dv_cpf(base))
    s = "".join(map(str, base))
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}" if formatado else s


_PESOS_CNPJ_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_CNPJ_2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def _dv_cnpj(digitos: list[int], pesos: tuple[int, ...]) -> int:
    resto = sum(d * p for d, p in zip(digitos, pesos)) % 11
    return 0 if resto < 2 else 11 - resto


def gerar_cnpj(rng: random.Random, formatado: bool = False, filial: int | None = None) -> str:
    """CNPJ numérico válido. `filial` (1..9999) fixa o sufixo de ordem; padrão 0001 (matriz)."""
    ordem = 1 if filial is None else filial
    if not 1 <= ordem <= 9999:
        raise ValueError("filial deve estar entre 1 e 9999")
    while True:
        raiz = [rng.randint(0, 9) for _ in range(8)]
        if len(set(raiz)) > 1:
            break
    base = raiz + [int(c) for c in f"{ordem:04d}"]
    base.append(_dv_cnpj(base, _PESOS_CNPJ_1))
    base.append(_dv_cnpj(base, _PESOS_CNPJ_2))
    s = "".join(map(str, base))
    if formatado:
        return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"
    return s


def gerar_lote_cpf(rng: random.Random, n: int) -> list[str]:
    """CPFs distintos."""
    vistos: set[str] = set()
    while len(vistos) < n:
        vistos.add(gerar_cpf(rng))
    return sorted(vistos)
