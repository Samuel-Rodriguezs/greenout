"""Contagem de vogais em um texto, ignorando acentos e maiúsculas."""

import unicodedata


def contar_vogais(texto: str) -> int:
    """Conta vogais (a, e, i, o, u), considerando letras acentuadas como a vogal base."""
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return sum(1 for c in decomposto if c in "aeiou")
