"""Jogo da velha com IA minimax."""
from typing import List, Optional

Tabuleiro = List[Optional[str]]
LINHAS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def novo_tabuleiro() -> Tabuleiro:
    return [None] * 9


def vencedor(t: Tabuleiro) -> Optional[str]:
    for a, b, c in LINHAS:
        if t[a] is not None and t[a] == t[b] == t[c]:
            return t[a]
    return None


def jogadas_validas(t: Tabuleiro) -> List[int]:
    return [i for i, v in enumerate(t) if v is None]


def jogar(t: Tabuleiro, pos: int, jogador: str) -> Tabuleiro:
    if jogador not in ("X", "O"):
        raise ValueError("jogador invalido")
    if not 0 <= pos < 9:
        raise ValueError("posicao fora do tabuleiro")
    if t[pos] is not None:
        raise ValueError("posicao ocupada")
    novo = list(t)
    novo[pos] = jogador
    return novo


def _minimax(t: Tabuleiro, vez: str, ia: str) -> int:
    v = vencedor(t)
    if v is not None:
        return 1 if v == ia else -1
    livres = jogadas_validas(t)
    if not livres:
        return 0
    prox = "O" if vez == "X" else "X"
    notas = [_minimax(jogar(t, p, vez), prox, ia) for p in livres]
    return max(notas) if vez == ia else min(notas)


def melhor_jogada(t: Tabuleiro, ia: str) -> int:
    livres = jogadas_validas(t)
    if not livres or vencedor(t) is not None:
        raise ValueError("jogo encerrado")
    adv = "O" if ia == "X" else "X"
    return max(livres, key=lambda p: _minimax(jogar(t, p, ia), adv, ia))
