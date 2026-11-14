"""Cifra de Vigenère e quebra por índice de coincidência + análise de frequência.

AVISO: cifra histórica, apenas para estudo.
"""
from __future__ import annotations

import string

A = string.ascii_uppercase

# Frequências relativas de letras em inglês (A..Z), em %.
FREQ_INGLES = [
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
    6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074,
]


def _validar_chave(chave: str) -> list[int]:
    ks = [ord(c) - 65 for c in chave.upper() if c in A]
    if not ks or len(ks) != len(chave):
        raise ValueError("chave deve conter apenas letras A-Z e não ser vazia")
    return ks


def _aplicar(texto: str, chave: str, sinal: int) -> str:
    ks = _validar_chave(chave)
    saida, i = [], 0
    for c in texto:
        if c.upper() in A and c.isascii():
            base = 65 if c.isupper() else 97
            saida.append(chr((ord(c) - base + sinal * ks[i % len(ks)]) % 26 + base))
            i += 1
        else:
            saida.append(c)
    return "".join(saida)


def cifrar(texto: str, chave: str) -> str:
    return _aplicar(texto, chave, 1)


def decifrar(texto: str, chave: str) -> str:
    return _aplicar(texto, chave, -1)


def _letras(texto: str) -> str:
    return "".join(c for c in texto.upper() if c in A)


def indice_coincidencia(texto: str) -> float:
    t = _letras(texto)
    n = len(t)
    if n < 2:
        return 0.0
    return sum(t.count(c) * (t.count(c) - 1) for c in A) / (n * (n - 1))


def estimar_tamanho_chave(texto: str, maximo: int = 12) -> int:
    """Menor tamanho cujo IC médio das colunas é próximo do inglês (~0.066)."""
    t = _letras(texto)
    medias = {}
    for k in range(1, maximo + 1):
        cols = [t[i::k] for i in range(k)]
        medias[k] = sum(indice_coincidencia(c) for c in cols) / k
    melhor = max(medias.values())
    for k in range(1, maximo + 1):
        if medias[k] >= melhor - 0.01:
            return k
    return 1


def _melhor_deslocamento(coluna: str) -> int:
    n = len(coluna) or 1
    melhor, melhor_chi = 0, float("inf")
    for s in range(26):
        chi = 0.0
        for i, letra in enumerate(A):
            obs = coluna.count(chr((i + s) % 26 + 65))
            esp = FREQ_INGLES[i] / 100 * n
            chi += (obs - esp) ** 2 / esp
        if chi < melhor_chi:
            melhor, melhor_chi = s, chi
    return melhor


def quebrar(texto: str, maximo: int = 12) -> tuple[str, str]:
    """Retorna (chave, texto_claro) assumindo texto em inglês."""
    t = _letras(texto)
    if len(t) < 2:
        raise ValueError("texto curto demais")
    k = estimar_tamanho_chave(texto, maximo)
    chave = "".join(chr(_melhor_deslocamento(t[i::k]) + 65) for i in range(k))
    return chave, decifrar(texto, chave)
