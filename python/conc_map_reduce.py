"""Map-reduce de contagem de palavras com multiprocessing.pool.ThreadPool."""
from __future__ import annotations

import re
from collections import Counter
from functools import reduce
from multiprocessing.pool import ThreadPool
from typing import Iterable

_PALAVRA = re.compile(r"\w+", re.UNICODE)


def mapear(texto: str) -> Counter:
    """Fase map: contagem local (minúsculas) de um pedaço de texto."""
    return Counter(p.lower() for p in _PALAVRA.findall(texto))


def reduzir(a: Counter, b: Counter) -> Counter:
    """Fase reduce: soma duas contagens parciais."""
    resultado = Counter(a)
    resultado.update(b)
    return resultado


def dividir(texto: str, partes: int) -> list[str]:
    """Divide o texto em até `partes` pedaços sem quebrar palavras."""
    if partes < 1:
        raise ValueError("partes deve ser >= 1")
    palavras = texto.split()
    if not palavras:
        return []
    tam = -(-len(palavras) // partes)
    return [" ".join(palavras[i : i + tam]) for i in range(0, len(palavras), tam)]


def contar_palavras(documentos: Iterable[str], workers: int = 4) -> Counter:
    docs = list(documentos)
    if not docs:
        return Counter()
    with ThreadPool(workers) as pool:
        parciais = pool.map(mapear, docs)
    return reduce(reduzir, parciais, Counter())


def contar_texto(texto: str, workers: int = 4) -> Counter:
    return contar_palavras(dividir(texto, workers), workers)


def mais_comuns(contagem: Counter, n: int) -> list[tuple[str, int]]:
    """Top-n com desempate alfabético (determinístico)."""
    return sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
