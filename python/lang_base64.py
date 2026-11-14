"""Codificação Base64 própria (RFC 4648), padrão e URL-safe, sem usar o módulo base64."""
from __future__ import annotations

_PADRAO = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_URL = _PADRAO[:-2] + "-_"


class ErroBase64(ValueError):
    """Entrada Base64 inválida."""


def codificar(dados: bytes, url_safe: bool = False, preenchimento: bool = True) -> str:
    alfa = _URL if url_safe else _PADRAO
    saida: list[str] = []
    for i in range(0, len(dados), 3):
        bloco = dados[i:i + 3]
        n = int.from_bytes(bloco.ljust(3, b"\0"), "big")
        chars = [alfa[(n >> s) & 63] for s in (18, 12, 6, 0)]
        validos = len(bloco) + 1
        saida.extend(chars[:validos])
        if preenchimento:
            saida.extend("=" * (4 - validos))
    return "".join(saida)


def decodificar(texto: str, url_safe: bool = False) -> bytes:
    alfa = _URL if url_safe else _PADRAO
    indice = {c: i for i, c in enumerate(alfa)}
    texto = "".join(texto.split())  # ignora espaços e quebras de linha
    dados = texto.rstrip("=")
    pad = len(texto) - len(dados)
    if pad > 2 or "=" in dados:
        raise ErroBase64("preenchimento '=' inválido")
    if pad and len(texto) % 4:
        raise ErroBase64("comprimento incorreto com preenchimento")
    if len(dados) % 4 == 1:
        raise ErroBase64("comprimento inválido")
    saida = bytearray()
    for i in range(0, len(dados), 4):
        bloco = dados[i:i + 4]
        n = 0
        for c in bloco:
            if c not in indice:
                raise ErroBase64(f"caractere inválido: {c!r}")
            n = (n << 6) | indice[c]
        faltam = 4 - len(bloco)
        n <<= 6 * faltam
        bytes_ = n.to_bytes(3, "big")[:3 - faltam]
        saida.extend(bytes_)
    return bytes(saida)
