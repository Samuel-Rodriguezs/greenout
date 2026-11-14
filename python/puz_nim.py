"""Jogo de Nim e teoria de Sprague-Grundy."""
from __future__ import annotations

from functools import lru_cache, reduce
from operator import xor
from typing import Callable, Optional


def nim_sum(pilhas: list[int]) -> int:
    return reduce(xor, pilhas, 0)


def jogada_vencedora(pilhas: list[int]) -> Optional[tuple[int, int]]:
    """(índice da pilha, quantidade a remover) que deixa nim-soma 0; None se perdedora."""
    s = nim_sum(pilhas)
    if s == 0:
        return None
    for i, p in enumerate(pilhas):
        alvo = p ^ s
        if alvo < p:
            return i, p - alvo
    return None  # inalcançável


def jogada_misere(pilhas: list[int]) -> Optional[tuple[int, int]]:
    """Nim misère: quem retira o último objeto perde."""
    if any(p > 1 for p in pilhas):
        grandes = sum(1 for p in pilhas if p > 1)
        if grandes == 1:
            i = next(k for k, p in enumerate(pilhas) if p > 1)
            uns = sum(1 for p in pilhas if p == 1)
            # deixar um número ímpar de pilhas unitárias
            alvo = 0 if uns % 2 == 1 else 1
            return i, pilhas[i] - alvo
        return jogada_vencedora(pilhas)
    uns = sum(1 for p in pilhas if p == 1)
    if uns % 2 == 1:  # só pilhas unitárias: com quantidade ímpar quem joga perde
        return None
    return next(k for k, p in enumerate(pilhas) if p == 1), 1


def mex(valores: set[int]) -> int:
    m = 0
    while m in valores:
        m += 1
    return m


def grundy(estado, movimentos: Callable) -> int:
    """Valor de Grundy de um jogo imparcial cujos sucessores vêm de `movimentos(estado)`."""

    @lru_cache(maxsize=None)
    def g(e) -> int:
        return mex({g(s) for s in movimentos(e)})

    return g(estado)


def grundy_subtracao(n: int, permitidos: tuple[int, ...]) -> int:
    """Pilha única em que se remove uma quantidade de `permitidos`."""
    tabela = [0] * (n + 1)
    for i in range(1, n + 1):
        tabela[i] = mex({tabela[i - k] for k in permitidos if k <= i})
    return tabela[n]


def vence_soma_de_jogos(valores_grundy: list[int]) -> bool:
    """Quem joga primeiro vence a soma de jogos imparciais iff o XOR dos Grundy != 0."""
    return nim_sum(valores_grundy) != 0


def grundy_kayles(n: int) -> int:
    """Kayles: remover 1 pino ou 2 adjacentes, o que pode dividir a fileira em duas."""
    g = [0] * (n + 1)
    for i in range(1, n + 1):
        opcoes = set()
        for k in (1, 2):
            if k <= i:
                for esq in range(0, i - k + 1):
                    opcoes.add(g[esq] ^ g[i - k - esq])
        g[i] = mex(opcoes)
    return g[n]
