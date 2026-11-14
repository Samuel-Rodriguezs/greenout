"""Placas de veículo: modelo antigo (ABC-1234) e Mercosul (ABC1D23)."""
from __future__ import annotations

import re

_ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")
_MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")


def normalizar_placa(placa: str) -> str:
    """Maiúsculas e sem hífen/espaços."""
    return re.sub(r"[-\s]", "", placa).upper()


def tipo_placa(placa: str) -> str | None:
    """Retorna 'antiga', 'mercosul' ou None se o formato for inválido."""
    n = normalizar_placa(placa)
    if _ANTIGA.match(n):
        return "antiga"
    if _MERCOSUL.match(n):
        return "mercosul"
    return None


def validar_placa(placa: str) -> bool:
    return tipo_placa(placa) is not None


def antiga_para_mercosul(placa: str) -> str:
    """Converte ABC1234 em ABC1D34: o segundo dígito numérico (0-9) vira a letra A-J."""
    n = normalizar_placa(placa)
    if tipo_placa(n) != "antiga":
        raise ValueError(f"não é uma placa no modelo antigo: {placa!r}")
    return n[:4] + chr(ord("A") + int(n[4])) + n[5:]


def mercosul_para_antiga(placa: str) -> str:
    """Operação inversa de antiga_para_mercosul (letra A-J volta a ser 0-9)."""
    n = normalizar_placa(placa)
    if tipo_placa(n) != "mercosul":
        raise ValueError(f"não é uma placa Mercosul: {placa!r}")
    letra = n[4]
    if not "A" <= letra <= "J":
        raise ValueError("a letra central só corresponde a dígito entre A e J")
    return n[:4] + str(ord(letra) - ord("A")) + n[5:]


def formatar_placa(placa: str) -> str:
    """Antiga com hífen (ABC-1234); Mercosul sem hífen (ABC1D23)."""
    n = normalizar_placa(placa)
    tipo = tipo_placa(n)
    if tipo is None:
        raise ValueError(f"placa inválida: {placa!r}")
    return f"{n[:3]}-{n[3:]}" if tipo == "antiga" else n
