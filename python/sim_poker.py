"""Baralho (embaralhar, distribuir) e avaliador de mãos de poker de 5 cartas."""
from __future__ import annotations

import random
from collections import Counter

NAIPES = "♣♦♥♠"
VALORES = "23456789TJQKA"
Carta = tuple[int, str]  # (valor 2..14, naipe)

CATEGORIAS = ["carta alta", "par", "dois pares", "trinca", "sequência", "flush", "full house",
              "quadra", "straight flush"]


def novo_baralho() -> list[Carta]:
    return [(v, n) for n in NAIPES for v in range(2, 15)]


def embaralhar(baralho: list[Carta], rng: random.Random) -> list[Carta]:
    copia = list(baralho)
    rng.shuffle(copia)
    return copia


def distribuir(baralho: list[Carta], n: int) -> tuple[list[Carta], list[Carta]]:
    """Retorna (mão, restante); não altera o baralho original."""
    if n > len(baralho):
        raise ValueError("cartas insuficientes")
    return baralho[:n], baralho[n:]


def parse_carta(texto: str) -> Carta:
    if len(texto) != 2 or texto[0].upper() not in VALORES or texto[1] not in NAIPES + "cdhs":
        raise ValueError(f"carta inválida: {texto!r}")
    naipe = dict(zip("cdhs", NAIPES)).get(texto[1], texto[1])
    return VALORES.index(texto[0].upper()) + 2, naipe


def parse_mao(texto: str) -> list[Carta]:
    return [parse_carta(t) for t in texto.split()]


def avaliar(mao: list[Carta]) -> tuple[int, tuple[int, ...]]:
    """Retorna (categoria 0-8, desempate) — comparável com <, > e ==."""
    if len(mao) != 5 or len(set(mao)) != 5:
        raise ValueError("a mão deve ter 5 cartas distintas")
    valores = sorted((v for v, _ in mao), reverse=True)
    flush = len({n for _, n in mao}) == 1
    unicos = sorted(set(valores), reverse=True)
    reta = len(unicos) == 5 and unicos[0] - unicos[4] == 4
    alta = unicos[0]
    if unicos == [14, 5, 4, 3, 2]:  # roda: A-2-3-4-5
        reta, alta = True, 5
    cont = Counter(valores)
    grupos = sorted(cont.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    padrao = [c for _, c in grupos]
    ordem = tuple(v for v, _ in grupos)
    if reta and flush:
        return 8, (alta,)
    if padrao == [4, 1]:
        return 7, ordem
    if padrao == [3, 2]:
        return 6, ordem
    if flush:
        return 5, tuple(valores)
    if reta:
        return 4, (alta,)
    if padrao == [3, 1, 1]:
        return 3, ordem
    if padrao == [2, 2, 1]:
        return 2, ordem
    if padrao == [2, 1, 1, 1]:
        return 1, ordem
    return 0, tuple(valores)


def nome_categoria(mao: list[Carta]) -> str:
    return CATEGORIAS[avaliar(mao)[0]]


def melhor_mao(cartas: list[Carta]) -> list[Carta]:
    """Melhor mão de 5 entre 5 a 7 cartas."""
    from itertools import combinations

    if not 5 <= len(cartas) <= 7:
        raise ValueError("informe de 5 a 7 cartas")
    return list(max(combinations(cartas, 5), key=avaliar))
