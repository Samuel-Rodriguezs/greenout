"""Nuvem de palavras: contagem das N palavras mais frequentes e tamanhos de fonte."""
from collections import Counter

from txt_stopwords import remover_stopwords
from txt_tokenizador import tokenizar


def top_palavras(texto: str, n: int = 10, sem_stopwords: bool = True, min_letras: int = 3) -> list[tuple[str, int]]:
    """Retorna [(palavra, contagem)] ordenado por contagem desc. e depois alfabeticamente."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    tokens = tokenizar(texto)
    if sem_stopwords:
        tokens = remover_stopwords(tokens)
    contagem = Counter(t for t in tokens if len(t) >= min_letras)
    return sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def tamanhos_fonte(pares: list[tuple[str, int]], minimo: int = 10, maximo: int = 40) -> dict[str, int]:
    """Escala linear das contagens para tamanhos de fonte entre `minimo` e `maximo`."""
    if not pares:
        return {}
    menor = min(c for _, c in pares)
    maior = max(c for _, c in pares)
    if maior == menor:
        return {p: maximo for p, _ in pares}
    return {p: round(minimo + (c - menor) * (maximo - minimo) / (maior - menor)) for p, c in pares}
