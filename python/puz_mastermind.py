"""Mastermind: avaliação de palpites e solver minimax (estratégia de Knuth simplificada)."""
from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Optional

Codigo = tuple[int, ...]
Resposta = tuple[int, int]  # (pinos pretos, pinos brancos)


def avaliar(segredo: Codigo, palpite: Codigo) -> Resposta:
    """Pretos: posição e cor certas. Brancos: cor certa em posição errada."""
    if len(segredo) != len(palpite):
        raise ValueError("tamanhos diferentes")
    pretos = sum(a == b for a, b in zip(segredo, palpite))
    comum = sum((Counter(segredo) & Counter(palpite)).values())
    return pretos, comum - pretos


def todos_codigos(cores: int, posicoes: int) -> list[Codigo]:
    return list(product(range(cores), repeat=posicoes))


def melhor_palpite(candidatos: list[Codigo], universo: list[Codigo]) -> Codigo:
    """Minimiza o pior caso de candidatos restantes; empate favorece palpite ainda possível."""
    if len(candidatos) <= 2:
        return candidatos[0]
    possiveis = set(candidatos)
    if len(candidatos) > 150:  # amostra determinística para manter o custo baixo
        universo = candidatos[:: len(candidatos) // 40 + 1]
    elif len(candidatos) > 30:
        universo = candidatos
    melhor: Optional[Codigo] = None
    melhor_chave = (1 << 30, 1, ())
    for p in universo:
        grupos = Counter(avaliar(c, p) for c in candidatos)
        chave = (max(grupos.values()), 0 if p in possiveis else 1, p)
        if chave < melhor_chave:
            melhor_chave, melhor = chave, p
    return melhor  # type: ignore[return-value]


def resolver(segredo: Codigo, cores: int = 6, posicoes: int = 4) -> list[Codigo]:
    """Sequência de palpites usada até acertar o segredo."""
    if len(segredo) != posicoes or any(not 0 <= x < cores for x in segredo):
        raise ValueError("segredo inválido")
    universo = todos_codigos(cores, posicoes)
    candidatos = universo[:]
    palpite: Codigo = tuple(i % cores for i in (0, 0, 1, 1, 2, 2, 3, 3)[:posicoes])
    historico = []
    while True:
        historico.append(palpite)
        resposta = avaliar(segredo, palpite)
        if resposta == (posicoes, 0):
            return historico
        candidatos = [c for c in candidatos if avaliar(c, palpite) == resposta]
        palpite = melhor_palpite(candidatos, universo)


def pior_caso(cores: int, posicoes: int) -> int:
    """Maior número de palpites sobre todos os segredos possíveis."""
    return max(len(resolver(s, cores, posicoes)) for s in todos_codigos(cores, posicoes))
