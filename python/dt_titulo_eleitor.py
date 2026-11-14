"""Validação de título de eleitor (12 dígitos: 8 de inscrição + 2 de UF + 2 verificadores)."""
from __future__ import annotations

import re

UFS = {
    1: "SP", 2: "MG", 3: "RJ", 4: "RS", 5: "BA", 6: "PR", 7: "CE", 8: "PE", 9: "SC",
    10: "GO", 11: "MA", 12: "PB", 13: "PA", 14: "ES", 15: "PI", 16: "RN", 17: "AL",
    18: "MT", 19: "MS", 20: "DF", 21: "SE", 22: "AM", 23: "RO", 24: "AC", 25: "AP",
    26: "RR", 27: "TO", 28: "ZZ",  # ZZ = eleitor no exterior
}


def normalizar_titulo(titulo: str) -> str:
    return re.sub(r"[.\-\s]", "", titulo)


def _dv(soma: int, uf: int) -> int:
    resto = soma % 11
    if resto == 10:
        return 0
    if resto == 0 and uf in (1, 2):  # exceção histórica para SP e MG
        return 1
    return resto


def calcular_digitos(base: str) -> str:
    """Dois dígitos verificadores a partir dos 10 primeiros dígitos (inscrição + UF)."""
    if not re.fullmatch(r"\d{10}", base):
        raise ValueError("a base deve ter 10 dígitos (8 de inscrição + 2 de UF)")
    uf = int(base[8:10])
    soma1 = sum(int(base[i]) * (i + 2) for i in range(8))
    dv1 = _dv(soma1, uf)
    soma2 = int(base[8]) * 7 + int(base[9]) * 8 + dv1 * 9
    dv2 = _dv(soma2, uf)
    return f"{dv1}{dv2}"


def validar_titulo(titulo: str) -> bool:
    n = normalizar_titulo(titulo)
    if not re.fullmatch(r"\d{12}", n):
        return False
    if int(n[8:10]) not in UFS:
        return False
    return calcular_digitos(n[:10]) == n[10:]


def uf_do_titulo(titulo: str) -> str:
    """Sigla da UF de emissão (ZZ para exterior). Exige título válido."""
    n = normalizar_titulo(titulo)
    if not validar_titulo(n):
        raise ValueError("título de eleitor inválido")
    return UFS[int(n[8:10])]


def gerar_titulo(inscricao: str, uf: int) -> str:
    """Monta um título válido a partir de 8 dígitos de inscrição e do código da UF."""
    if not re.fullmatch(r"\d{8}", inscricao):
        raise ValueError("a inscrição deve ter 8 dígitos")
    if uf not in UFS:
        raise ValueError("código de UF inválido")
    base = f"{inscricao}{uf:02d}"
    return base + calcular_digitos(base)
