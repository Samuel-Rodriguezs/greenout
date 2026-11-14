"""Inversão da ordem das palavras de uma frase."""


def inverter_palavras(frase: str) -> str:
    """Inverte a ordem das palavras; espaços repetidos nas pontas e no meio são normalizados."""
    return " ".join(reversed(frase.split()))
