"""Endereços IPv4: parse, formatação, classes, máscaras e faixas especiais."""
from __future__ import annotations


def parse_ipv4(texto: str) -> int:
    """Converte 'a.b.c.d' em inteiro de 32 bits. Rejeita octetos inválidos."""
    partes = texto.strip().split(".")
    if len(partes) != 4:
        raise ValueError(f"IPv4 inválido: {texto!r}")
    valor = 0
    for p in partes:
        if not p.isascii() or not p.isdigit() or (len(p) > 1 and p[0] == "0"):
            raise ValueError(f"octeto inválido: {p!r}")
        n = int(p)
        if n > 255:
            raise ValueError(f"octeto fora da faixa: {n}")
        valor = (valor << 8) | n
    return valor


def formatar_ipv4(valor: int) -> str:
    if not 0 <= valor <= 0xFFFFFFFF:
        raise ValueError("valor fora de 32 bits")
    return ".".join(str((valor >> s) & 0xFF) for s in (24, 16, 8, 0))


def classe_ipv4(valor: int) -> str:
    """Classe histórica (A-E) pelo primeiro octeto."""
    primeiro = valor >> 24
    if primeiro < 128:
        return "A"
    if primeiro < 192:
        return "B"
    if primeiro < 224:
        return "C"
    if primeiro < 240:
        return "D"
    return "E"


def mascara_de_prefixo(prefixo: int) -> int:
    if not 0 <= prefixo <= 32:
        raise ValueError("prefixo deve estar entre 0 e 32")
    return (0xFFFFFFFF << (32 - prefixo)) & 0xFFFFFFFF


def prefixo_de_mascara(mascara: int) -> int:
    """Número de bits 1 de uma máscara; exige máscara contígua."""
    inv = ~mascara & 0xFFFFFFFF
    if inv & (inv + 1):
        raise ValueError("máscara não contígua")
    return 32 - inv.bit_length()


_PRIVADAS = (("10.0.0.0", 8), ("172.16.0.0", 12), ("192.168.0.0", 16))


def _em(valor: int, base: str, prefixo: int) -> bool:
    m = mascara_de_prefixo(prefixo)
    return (valor & m) == (parse_ipv4(base) & m)


def eh_privado(valor: int) -> bool:
    return any(_em(valor, b, p) for b, p in _PRIVADAS)


def eh_loopback(valor: int) -> bool:
    return _em(valor, "127.0.0.0", 8)


def eh_link_local(valor: int) -> bool:
    return _em(valor, "169.254.0.0", 16)


def eh_multicast(valor: int) -> bool:
    return _em(valor, "224.0.0.0", 4)
