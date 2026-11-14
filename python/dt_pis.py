"""Validação e formatação de PIS/PASEP/NIT (11 dígitos, módulo 11)."""
from __future__ import annotations

import re

_PESOS = (3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def normalizar_pis(pis: str) -> str:
    return re.sub(r"[.\-\s]", "", pis)


def calcular_digito(base: str) -> int:
    """Dígito verificador para os 10 primeiros dígitos."""
    if not re.fullmatch(r"\d{10}", base):
        raise ValueError("a base do PIS deve ter 10 dígitos")
    resto = sum(int(c) * p for c, p in zip(base, _PESOS)) % 11
    return 0 if resto < 2 else 11 - resto


def validar_pis(pis: str) -> bool:
    n = normalizar_pis(pis)
    if not re.fullmatch(r"\d{11}", n) or len(set(n)) == 1:
        return False
    return calcular_digito(n[:10]) == int(n[10])


def formatar_pis(pis: str) -> str:
    n = normalizar_pis(pis)
    if not re.fullmatch(r"\d{11}", n):
        raise ValueError("PIS deve ter 11 dígitos")
    return f"{n[:3]}.{n[3:8]}.{n[8:10]}-{n[10]}"


def gerar_pis(base: str) -> str:
    base = normalizar_pis(base)
    return base + str(calcular_digito(base))
