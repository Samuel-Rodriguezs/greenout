"""Resumo extrativo por frequência de palavras."""
from collections import Counter

from txt_stopwords import remover_stopwords
from txt_tokenizador import tokenizar, tokenizar_sentencas


def pontuar_sentencas(texto: str) -> list[tuple[str, float]]:
    """Pontua cada sentença: média da frequência de suas palavras de conteúdo."""
    sentencas = tokenizar_sentencas(texto)
    conteudos = [remover_stopwords(tokenizar(s)) for s in sentencas]
    freq = Counter(t for c in conteudos for t in c)
    resultado = []
    for s, c in zip(sentencas, conteudos):
        pontos = sum(freq[t] for t in c) / len(c) if c else 0.0
        resultado.append((s, pontos))
    return resultado


def resumir(texto: str, n: int = 2) -> str:
    """Seleciona as `n` melhores sentenças, mantendo a ordem original."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    pontuadas = pontuar_sentencas(texto)
    melhores = sorted(range(len(pontuadas)), key=lambda i: (-pontuadas[i][1], i))[:n]
    return " ".join(pontuadas[i][0] for i in sorted(melhores))
