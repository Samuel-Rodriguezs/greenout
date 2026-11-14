"""Base32 (RFC 4648) próprio: alfabeto padrão e Extended Hex, com padding."""
from __future__ import annotations

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
ALFABETO_HEX = "0123456789ABCDEFGHIJKLMNOPQRSTUV"


class ErroBase32(ValueError):
    """Entrada Base32 inválida."""


def codificar(dados: bytes, alfabeto: str = ALFABETO, padding: bool = True) -> str:
    saida: list[str] = []
    buffer = bits = 0
    for b in dados:
        buffer = (buffer << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            saida.append(alfabeto[(buffer >> bits) & 31])
        buffer &= (1 << bits) - 1
    if bits:
        saida.append(alfabeto[(buffer << (5 - bits)) & 31])
    if padding:
        saida.append("=" * (-len(saida) % 8))
    return "".join(saida)


def decodificar(texto: str, alfabeto: str = ALFABETO) -> bytes:
    """Decodifica (maiúsculas/minúsculas aceitas); rejeita caracteres fora do alfabeto,
    padding mal posicionado e bits finais não nulos."""
    t = texto.rstrip("=")
    if len(texto) - len(t) > 6:
        raise ErroBase32("padding demais")
    if "=" in t:
        raise ErroBase32("'=' no meio do texto")
    if len(texto) != len(t) and len(texto) % 8:
        raise ErroBase32("padding incorreto")
    if len(t) % 8 in (1, 3, 6):
        raise ErroBase32("comprimento inválido")
    mapa = {c: i for i, c in enumerate(alfabeto)}
    saida = bytearray()
    buffer = bits = 0
    for c in t.upper():
        if c not in mapa:
            raise ErroBase32(f"caractere inválido: {c!r}")
        buffer = (buffer << 5) | mapa[c]
        bits += 5
        if bits >= 8:
            bits -= 8
            saida.append((buffer >> bits) & 0xFF)
            buffer &= (1 << bits) - 1
    if buffer:
        raise ErroBase32("bits finais não nulos")
    return bytes(saida)
