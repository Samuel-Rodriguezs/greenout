"""Remoção de stopwords do português brasileiro (lista pequena embutida)."""
import re

STOPWORDS_PT: frozenset[str] = frozenset("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre
e ou mas que se como quando onde porque pois também já não mais muito muita ao aos à às
é são foi era ser estar está estão tem têm ter há eu tu ele ela nós vocês eles elas me te
lhe meu minha seu sua isso isto esse essa este esta aquele aquela até entre
""".split())


def e_stopword(palavra: str) -> bool:
    return palavra.lower() in STOPWORDS_PT


def remover_stopwords(tokens: list[str], extras: set[str] | None = None) -> list[str]:
    """Filtra stopwords de uma lista de tokens (sem diferenciar caixa)."""
    extras_min = {e.lower() for e in (extras or set())}
    return [t for t in tokens if t.lower() not in STOPWORDS_PT and t.lower() not in extras_min]


def remover_stopwords_texto(texto: str) -> str:
    palavras = re.findall(r"\w+(?:-\w+)*", texto, re.UNICODE)
    return " ".join(remover_stopwords(palavras))
