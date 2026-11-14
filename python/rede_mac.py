"""Endereços MAC (48 bits) e identificador de interface EUI-64."""
from __future__ import annotations

import re

_SEP = re.compile(r"[:\-.]")


def parse_mac(texto: str) -> int:
    """Aceita aa:bb:cc:dd:ee:ff, aa-bb-..., aabb.ccdd.eeff ou 12 dígitos."""
    t = texto.strip()
    if ":" in t or "-" in t:
        partes = re.split(r"[:\-]", t)
        if len(partes) != 6 or any(len(p) != 2 for p in partes):
            raise ValueError(f"MAC inválido: {texto!r}")
        hexa = "".join(partes)
    elif "." in t:
        partes = t.split(".")
        if len(partes) != 3 or any(len(p) != 4 for p in partes):
            raise ValueError(f"MAC inválido: {texto!r}")
        hexa = "".join(partes)
    else:
        hexa = t
    if len(hexa) != 12 or any(c not in "0123456789abcdefABCDEF" for c in hexa):
        raise ValueError(f"MAC inválido: {texto!r}")
    return int(hexa, 16)


def formatar_mac(valor: int, sep: str = ":", maiusculo: bool = False) -> str:
    if not 0 <= valor < (1 << 48):
        raise ValueError("valor fora de 48 bits")
    hexa = f"{valor:012x}"
    if maiusculo:
        hexa = hexa.upper()
    return sep.join(hexa[i:i + 2] for i in range(0, 12, 2))


def eh_multicast(mac: int) -> bool:
    """Bit I/G (menos significativo do primeiro octeto)."""
    return bool((mac >> 40) & 0x01)


def eh_local(mac: int) -> bool:
    """Bit U/L: endereço administrado localmente."""
    return bool((mac >> 40) & 0x02)


def eh_broadcast(mac: int) -> bool:
    return mac == 0xFFFFFFFFFFFF


def oui(mac: int) -> int:
    return mac >> 24


def eui64(mac: int) -> int:
    """MAC -> EUI-64 modificado: insere FFFE no meio e inverte o bit U/L."""
    alto, baixo = mac >> 24, mac & 0xFFFFFF
    return (((alto ^ 0x020000) << 40) | (0xFFFE << 24) | baixo)


def mac_de_eui64(valor: int) -> int:
    if (valor >> 24) & 0xFFFF != 0xFFFE:
        raise ValueError("EUI-64 não derivado de MAC (falta FFFE)")
    alto = (valor >> 40) ^ 0x020000
    return (alto << 24) | (valor & 0xFFFFFF)


def link_local_ipv6(mac: int) -> str:
    """Endereço IPv6 link-local gerado por SLAAC a partir do MAC."""
    e = eui64(mac)
    grupos = [(e >> s) & 0xFFFF for s in (48, 32, 16, 0)]
    return "fe80::" + ":".join(f"{g:x}" for g in grupos)
