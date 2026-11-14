"""Poker Hands Kata: comparar duas mãos de cinco cartas (ex.: "2H 3D 5S 9C KD")."""
from __future__ import annotations

from collections import Counter

_VALORES = {v: i for i, v in enumerate("23456789TJQKA", start=2)}
_NAIPES = "CDHS"
NOMES = ["Carta Alta", "Par", "Dois Pares", "Trinca", "Sequência", "Flush",
         "Full House", "Quadra", "Straight Flush"]


def _parse(mao: str) -> list[tuple[int, str]]:
    cartas = mao.split()
    if len(cartas) != 5:
        raise ValueError("a mão deve ter 5 cartas")
    resultado = []
    for c in cartas:
        if len(c) != 2 or c[0] not in _VALORES or c[1] not in _NAIPES:
            raise ValueError(f"carta inválida: {c}")
        resultado.append((_VALORES[c[0]], c[1]))
    if len(set(resultado)) != 5:
        raise ValueError("cartas repetidas na mão")
    return resultado


def avaliar(mao: str) -> tuple[int, list[int]]:
    """Retorna (categoria, desempates). Categoria indexa NOMES."""
    cartas = _parse(mao)
    valores = sorted((v for v, _ in cartas), reverse=True)
    flush = len({n for _, n in cartas}) == 1
    # Roda A-2-3-4-5: o ás vale 1.
    if valores == [14, 5, 4, 3, 2]:
        valores_seq = [5, 4, 3, 2, 1]
        sequencia = True
    else:
        valores_seq = valores
        sequencia = all(valores[i] - 1 == valores[i + 1] for i in range(4))
    cont = Counter(valores)
    # Ordena valores por (quantidade, valor) decrescente.
    agrupados = sorted(cont.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    ordem = [v for v, _ in agrupados]
    formato = sorted(cont.values(), reverse=True)
    if sequencia and flush:
        return 8, valores_seq
    if formato == [4, 1]:
        return 7, ordem
    if formato == [3, 2]:
        return 6, ordem
    if flush:
        return 5, valores
    if sequencia:
        return 4, valores_seq
    if formato == [3, 1, 1]:
        return 3, ordem
    if formato == [2, 2, 1]:
        return 2, ordem
    if formato == [2, 1, 1, 1]:
        return 1, ordem
    return 0, valores


def nome_da_mao(mao: str) -> str:
    return NOMES[avaliar(mao)[0]]


def comparar(mao1: str, mao2: str) -> int:
    """1 se a mão 1 vence, 2 se a mão 2 vence, 0 em empate."""
    a, b = avaliar(mao1), avaliar(mao2)
    if a > b:
        return 1
    if b > a:
        return 2
    return 0
