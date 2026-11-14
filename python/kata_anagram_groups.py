"""Anagram Groups Kata: agrupar palavras que são anagramas entre si."""
from __future__ import annotations

import unicodedata
from collections import defaultdict


def _chave(palavra: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", palavra.lower())
        if not unicodedata.combining(c)
    )
    return "".join(sorted(c for c in sem_acento if c.isalnum()))


def agrupar(palavras: list[str], minimo: int = 1) -> list[list[str]]:
    """Agrupa anagramas (ignora caixa e acentos); mantém a ordem de primeira aparição.

    Grupos com menos de `minimo` palavras são descartados; duplicatas exatas
    dentro de um grupo são removidas.
    """
    if minimo < 1:
        raise ValueError("minimo deve ser >= 1")
    grupos: dict[str, list[str]] = defaultdict(list)
    for p in palavras:
        chave = _chave(p)
        if not chave:
            continue
        if p not in grupos[chave]:
            grupos[chave].append(p)
    return [g for g in grupos.values() if len(g) >= minimo]


def maior_grupo(palavras: list[str]) -> list[str]:
    grupos = agrupar(palavras)
    return max(grupos, key=len) if grupos else []
