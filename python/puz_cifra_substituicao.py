"""Cifra de substituição simples: cifrar, decifrar e quebrar por frequência + hill climbing."""
from __future__ import annotations

import math
import random
import string
from collections import Counter

ALFABETO = string.ascii_lowercase

# Frequência aproximada das letras em português (%)
FREQ_PT = {
    "a": 14.6, "b": 1.0, "c": 3.9, "d": 5.0, "e": 12.6, "f": 1.0, "g": 1.3, "h": 1.3,
    "i": 6.2, "j": 0.4, "k": 0.02, "l": 2.8, "m": 4.7, "n": 5.0, "o": 10.7, "p": 2.5,
    "q": 1.2, "r": 6.5, "s": 7.8, "t": 4.3, "u": 4.6, "v": 1.7, "w": 0.01, "x": 0.2,
    "y": 0.01, "z": 0.5,
}
_LOG_FREQ = {c: math.log(f / 100) for c, f in FREQ_PT.items()}


def chave_aleatoria(seed: int) -> str:
    letras = list(ALFABETO)
    random.Random(seed).shuffle(letras)
    return "".join(letras)


def _validar(chave: str) -> None:
    if sorted(chave) != list(ALFABETO):
        raise ValueError("a chave deve ser uma permutação de a-z")


def cifrar(texto: str, chave: str) -> str:
    _validar(chave)
    tabela = {a: c for a, c in zip(ALFABETO, chave)}
    return "".join(_manter_caixa(ch, tabela) for ch in texto)


def decifrar(texto: str, chave: str) -> str:
    _validar(chave)
    tabela = {c: a for a, c in zip(ALFABETO, chave)}
    return "".join(_manter_caixa(ch, tabela) for ch in texto)


def _manter_caixa(ch: str, tabela: dict[str, str]) -> str:
    if ch.lower() in tabela:
        novo = tabela[ch.lower()]
        return novo.upper() if ch.isupper() else novo
    return ch


def contar_letras(texto: str) -> Counter:
    return Counter(c for c in texto.lower() if c in ALFABETO)


def chave_por_frequencia(cifrado: str) -> str:
    """Chave inicial: letra mais frequente do cifrado -> letra mais frequente do português."""
    cont = contar_letras(cifrado)
    cifradas = sorted(ALFABETO, key=lambda c: (-cont[c], c))
    claras = sorted(ALFABETO, key=lambda c: (-FREQ_PT[c], c))
    mapa = dict(zip(claras, cifradas))  # letra clara -> letra cifrada
    return "".join(mapa[a] for a in ALFABETO)


def pontuacao(texto: str, bigramas: dict[str, float]) -> float:
    """Log-verossimilhança com frequências de letras e bigramas conhecidos."""
    letras = [c for c in texto.lower() if c in ALFABETO]
    total = sum(_LOG_FREQ[c] for c in letras)
    for a, b in zip(letras, letras[1:]):
        total += bigramas.get(a + b, -9.0)
    return total


def modelo_bigramas(corpus: str) -> dict[str, float]:
    """Log-probabilidades de bigramas estimadas de um corpus de referência."""
    letras = [c for c in corpus.lower() if c in ALFABETO]
    cont = Counter(a + b for a, b in zip(letras, letras[1:]))
    n = sum(cont.values())
    return {bg: math.log(v / n) for bg, v in cont.items()}


def quebrar(cifrado: str, bigramas: dict[str, float], seed: int = 0,
            reinicios: int = 4, iteracoes: int = 1500) -> tuple[str, str]:
    """Hill climbing sobre a chave a partir da chave por frequência; devolve (chave, texto claro).

    A pontuação usa contagens de unigramas/bigramas do cifrado (evita redecifrar o texto a cada passo).
    """
    letras = [c for c in cifrado.lower() if c in ALFABETO]
    uni = Counter(letras)
    bi = Counter(a + b for a, b in zip(letras, letras[1:]))

    def pont(chave: list[str]) -> float:
        # chave[i] = letra cifrada que representa ALFABETO[i]; inverso: cifrada -> clara
        inv = {c: ALFABETO[i] for i, c in enumerate(chave)}
        total = sum(n * _LOG_FREQ[inv[c]] for c, n in uni.items())
        for par, n in bi.items():
            total += n * bigramas.get(inv[par[0]] + inv[par[1]], -9.0)
        return total

    rng = random.Random(seed)
    melhor_chave, melhor_pont = "", -math.inf
    for r in range(reinicios):
        chave = list(chave_por_frequencia(cifrado))
        for _ in range(r * 4):  # reinícios perturbam a solução inicial
            i, j = rng.sample(range(26), 2)
            chave[i], chave[j] = chave[j], chave[i]
        atual = pont(chave)
        for _ in range(iteracoes):
            i, j = rng.sample(range(26), 2)
            chave[i], chave[j] = chave[j], chave[i]
            nova = pont(chave)
            if nova > atual:
                atual = nova
            else:
                chave[i], chave[j] = chave[j], chave[i]
        if atual > melhor_pont:
            melhor_pont, melhor_chave = atual, "".join(chave)
    return melhor_chave, decifrar(cifrado, melhor_chave)
