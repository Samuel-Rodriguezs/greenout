"""Base64 / Base64url e hexlify implementados à mão (sem base64/binascii)."""
from __future__ import annotations

_STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_URL = _STD[:-2] + "-_"
_HEX = "0123456789abcdef"


def _codificar(dados: bytes, alfabeto: str, padding: bool) -> str:
    saida = []
    for i in range(0, len(dados), 3):
        bloco = dados[i : i + 3]
        n = int.from_bytes(bloco.ljust(3, b"\x00"), "big")
        chars = [alfabeto[(n >> s) & 63] for s in (18, 12, 6, 0)]
        validos = len(bloco) + 1
        saida.append("".join(chars[:validos]) + ("=" * (4 - validos) if padding else ""))
    return "".join(saida)


def _decodificar(texto: str, alfabeto: str) -> bytes:
    texto = texto.rstrip("=")
    if len(texto) % 4 == 1:
        raise ValueError("comprimento base64 inválido")
    tab = {c: i for i, c in enumerate(alfabeto)}
    saida = bytearray()
    for i in range(0, len(texto), 4):
        bloco = texto[i : i + 4]
        try:
            n = 0
            for c in bloco:
                n = (n << 6) | tab[c]
        except KeyError as e:
            raise ValueError(f"caractere inválido: {e.args[0]!r}") from None
        n <<= 6 * (4 - len(bloco))
        saida += n.to_bytes(3, "big")[: len(bloco) - 1]
    return bytes(saida)


def b64_codificar(dados: bytes) -> str:
    return _codificar(dados, _STD, True)


def b64_decodificar(texto: str) -> bytes:
    return _decodificar(texto, _STD)


def b64url_codificar(dados: bytes, padding: bool = False) -> str:
    return _codificar(dados, _URL, padding)


def b64url_decodificar(texto: str) -> bytes:
    return _decodificar(texto, _URL)


def hexlify(dados: bytes) -> str:
    return "".join(_HEX[b >> 4] + _HEX[b & 15] for b in dados)


def unhexlify(texto: str) -> bytes:
    if len(texto) % 2:
        raise ValueError("comprimento ímpar")
    baixo = texto.lower()
    if any(c not in _HEX for c in baixo):
        raise ValueError("hex inválido")
    return bytes(_HEX.index(baixo[i]) << 4 | _HEX.index(baixo[i + 1]) for i in range(0, len(baixo), 2))
