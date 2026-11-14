"""Verificação de palíndromos em frases."""

import unicodedata


def eh_palindromo(texto: str) -> bool:
    """Ignora acentos, maiúsculas, espaços e pontuação; texto vazio é palíndromo."""
    base = unicodedata.normalize("NFD", texto.lower())
    letras = [c for c in base if c.isalnum()]
    return letras == letras[::-1]
