def eh_palindromo(texto: str) -> bool:
    """Ignora maiúsculas, espaços e pontuação."""
    limpo = [c.lower() for c in texto if c.isalnum()]
    return limpo == limpo[::-1]
