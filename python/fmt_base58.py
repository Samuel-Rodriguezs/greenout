"""Base58 e Base58Check (alfabeto do Bitcoin) próprios."""
from __future__ import annotations

import hashlib

ALFABETO = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_INDICE = {c: i for i, c in enumerate(ALFABETO)}


class ErroBase58(ValueError):
    """Entrada Base58 inválida."""


def codificar(dados: bytes) -> str:
    zeros = len(dados) - len(dados.lstrip(b"\x00"))
    n = int.from_bytes(dados, "big")
    saida: list[str] = []
    while n:
        n, r = divmod(n, 58)
        saida.append(ALFABETO[r])
    return "1" * zeros + "".join(reversed(saida))


def decodificar(texto: str) -> bytes:
    n = 0
    for c in texto:
        if c not in _INDICE:
            raise ErroBase58(f"caractere inválido: {c!r}")
        n = n * 58 + _INDICE[c]
    zeros = len(texto) - len(texto.lstrip("1"))
    corpo = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * zeros + corpo


def _checksum(dados: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(dados).digest()).digest()[:4]


def codificar_check(dados: bytes) -> str:
    """Base58Check: anexa 4 bytes de checksum (duplo SHA-256)."""
    return codificar(dados + _checksum(dados))


def decodificar_check(texto: str) -> bytes:
    bruto = decodificar(texto)
    if len(bruto) < 4:
        raise ErroBase58("dados curtos demais para checksum")
    dados, soma = bruto[:-4], bruto[-4:]
    if _checksum(dados) != soma:
        raise ErroBase58("checksum inválido")
    return dados
