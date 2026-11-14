"""Validação do número de registro da CNH (11 dígitos, dois verificadores)."""
from __future__ import annotations

import re


def normalizar_cnh(cnh: str) -> str:
    return re.sub(r"[.\-\s]", "", cnh)


def calcular_digitos(base: str) -> str:
    """Dígitos verificadores para os 9 primeiros dígitos da CNH."""
    if not re.fullmatch(r"\d{9}", base):
        raise ValueError("a base da CNH deve ter 9 dígitos")
    d = [int(c) for c in base]
    desconto = 0
    soma = sum(d[i] * (9 - i) for i in range(9))
    dv1 = soma % 11
    if dv1 >= 10:
        dv1 = 0
        desconto = 2
    soma = sum(d[i] * (1 + i) for i in range(9))
    dv2 = (soma % 11) - desconto
    if dv2 < 0:
        dv2 += 11
    if dv2 >= 10:
        dv2 = 0
    return f"{dv1}{dv2}"


def validar_cnh(cnh: str) -> bool:
    n = normalizar_cnh(cnh)
    if not re.fullmatch(r"\d{11}", n) or len(set(n)) == 1:
        return False
    return calcular_digitos(n[:9]) == n[9:]


def gerar_cnh(base: str) -> str:
    base = normalizar_cnh(base)
    return base + calcular_digitos(base)
