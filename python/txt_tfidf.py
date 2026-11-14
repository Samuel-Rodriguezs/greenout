"""TF-IDF sobre uma coleção de documentos já tokenizados."""
import math
from collections import Counter


def tf(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    total = len(tokens)
    return {t: c / total for t, c in Counter(tokens).items()}


def idf(corpus: list[list[str]]) -> dict[str, float]:
    """IDF suavizado: ln((1+N)/(1+df)) + 1."""
    n = len(corpus)
    df: Counter = Counter()
    for doc in corpus:
        df.update(set(doc))
    return {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}


def tfidf(corpus: list[list[str]]) -> list[dict[str, float]]:
    pesos = idf(corpus)
    return [{t: v * pesos[t] for t, v in tf(doc).items()} for doc in corpus]


def termos_principais(vetor: dict[str, float], n: int = 3) -> list[str]:
    ordem = sorted(vetor.items(), key=lambda kv: (-kv[1], kv[0]))
    return [t for t, _ in ordem[:n]]
