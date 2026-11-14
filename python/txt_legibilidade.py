"""Índice de legibilidade Flesch adaptado ao português (Martins et al.)."""
from txt_silabas import contar_silabas
from txt_tokenizador import tokenizar, tokenizar_sentencas


def flesch_pt(texto: str) -> float:
    """248,835 - 1,015 * (palavras/sentenças) - 84,6 * (sílabas/palavras)."""
    palavras = tokenizar(texto)
    if not palavras:
        raise ValueError("texto sem palavras")
    sentencas = max(1, len(tokenizar_sentencas(texto)))
    silabas = sum(contar_silabas(p) for p in palavras)
    return 248.835 - 1.015 * (len(palavras) / sentencas) - 84.6 * (silabas / len(palavras))


def classificar(indice: float) -> str:
    if indice >= 75:
        return "muito fácil"
    if indice >= 50:
        return "fácil"
    if indice >= 25:
        return "difícil"
    return "muito difícil"


def nivel_texto(texto: str) -> str:
    return classificar(flesch_pt(texto))
