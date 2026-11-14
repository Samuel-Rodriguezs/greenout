"""Lights Out: solução por eliminação de Gauss em GF(2) usando inteiros como bitsets."""
from __future__ import annotations

from typing import Optional


def _mascara_botao(i: int, linhas: int, colunas: int) -> int:
    r, c = divmod(i, colunas)
    m = 1 << i
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < linhas and 0 <= nc < colunas:
            m |= 1 << (nr * colunas + nc)
    return m


def resolver(luzes: list[list[int]]) -> Optional[list[list[int]]]:
    """Retorna a grade de botões (0/1) a apertar para apagar tudo, ou None se impossível.

    Entre as soluções possíveis devolve a de variáveis livres iguais a zero.
    """
    linhas = len(luzes)
    colunas = len(luzes[0]) if linhas else 0
    n = linhas * colunas
    if n == 0:
        return []
    alvo = sum((luzes[r][c] & 1) << (r * colunas + c) for r in range(linhas) for c in range(colunas))
    # Sistema A x = alvo; cada equação i (luz i) tem bits nos botões que a afetam (matriz simétrica).
    # Linha = (máscara das variáveis, termo constante).
    eq = [(_mascara_botao(i, linhas, colunas), alvo >> i & 1) for i in range(n)]
    pivos: dict[int, int] = {}  # coluna pivô -> índice da linha
    eq = [list(e) for e in eq]
    usadas = 0
    for col in range(n):
        escolha = next((k for k in range(usadas, n) if eq[k][0] >> col & 1), None)
        if escolha is None:
            continue
        eq[usadas], eq[escolha] = eq[escolha], eq[usadas]
        for k in range(n):
            if k != usadas and eq[k][0] >> col & 1:
                eq[k][0] ^= eq[usadas][0]
                eq[k][1] ^= eq[usadas][1]
        pivos[col] = usadas
        usadas += 1
    if any(m == 0 and b for m, b in eq):
        return None
    x = 0
    for col, k in pivos.items():
        if eq[k][1]:
            x |= 1 << col
    return [[x >> (r * colunas + c) & 1 for c in range(colunas)] for r in range(linhas)]


def aplicar(luzes: list[list[int]], botoes: list[list[int]]) -> list[list[int]]:
    linhas, colunas = len(luzes), len(luzes[0])
    saida = [l[:] for l in luzes]
    for r in range(linhas):
        for c in range(colunas):
            if botoes[r][c]:
                for dr, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < linhas and 0 <= nc < colunas:
                        saida[nr][nc] ^= 1
    return saida


def dimensao_do_nucleo(linhas: int, colunas: int) -> int:
    """Número de variáveis livres: quantas configurações 'silenciosas' existem (2^d)."""
    n = linhas * colunas
    base = [_mascara_botao(i, linhas, colunas) for i in range(n)]
    rank = 0
    for col in range(n):
        piv = next((k for k in range(rank, n) if base[k] >> col & 1), None)
        if piv is None:
            continue
        base[rank], base[piv] = base[piv], base[rank]
        for k in range(n):
            if k != rank and base[k] >> col & 1:
                base[k] ^= base[rank]
        rank += 1
    return n - rank
