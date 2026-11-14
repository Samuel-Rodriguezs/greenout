"""Tokenização de texto em português com suporte a acentos."""
import re

_PALAVRA = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", re.UNICODE)
_SENTENCA = re.compile(r"(?<=[.!?…])\s+")


def tokenizar(texto: str, minusculas: bool = True) -> list[str]:
    """Extrai palavras (letras Unicode, com hífen/apóstrofo internos)."""
    if minusculas:
        texto = texto.lower()
    return _PALAVRA.findall(texto)


def tokenizar_sentencas(texto: str) -> list[str]:
    """Divide o texto em sentenças pela pontuação final."""
    return [s.strip() for s in _SENTENCA.split(texto.strip()) if s.strip()]
