"""Validação, geração de dígitos e formatação de CNPJ (numérico e alfanumérico, IN RFB 2.229/2024)."""
from __future__ import annotations

import re

_PESOS_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_SEPARADORES = re.compile(r"[.\-/\s]")


def normalizar(cnpj: str) -> str:
    """Remove pontos, barra, hífen e espaços; letras ficam em maiúsculas."""
    return _SEPARADORES.sub("", cnpj).upper()


def _valor(c: str) -> int:
    return ord(c) - 48  # '0'..'9' -> 0..9 e 'A'..'Z' -> 17..42


def _digito(base: str, pesos: tuple[int, ...]) -> int:
    soma = sum(_valor(c) * p for c, p in zip(base, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def calcular_digitos(base: str) -> str:
    """Dois dígitos verificadores para a base de 12 caracteres (raiz + ordem)."""
    base = normalizar(base)
    if len(base) != 12 or not re.fullmatch(r"[0-9A-Z]{12}", base):
        raise ValueError("a base do CNPJ deve ter 12 caracteres alfanuméricos")
    d1 = _digito(base, _PESOS_1)
    d2 = _digito(base + str(d1), _PESOS_2)
    return f"{d1}{d2}"


def validar_cnpj(cnpj: str) -> bool:
    n = normalizar(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", n):
        return False
    if len(set(n)) == 1:  # sequências repetidas (00000000000000 etc.)
        return False
    return calcular_digitos(n[:12]) == n[12:]


def formatar_cnpj(cnpj: str) -> str:
    n = normalizar(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", n):
        raise ValueError("CNPJ deve ter 14 caracteres (12 alfanuméricos + 2 dígitos)")
    return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"


def gerar_cnpj(base: str) -> str:
    """Completa uma base de 12 caracteres com os dígitos verificadores."""
    base = normalizar(base)
    return base + calcular_digitos(base)
