"""Kakuro: molde de células brancas ('.') e pretas ('#') + somas das sequências; solver por backtracking."""
from __future__ import annotations

from itertools import combinations
from typing import Optional

Celula = tuple[int, int]
# Pistas: (direção 'H' ou 'V', (linha, coluna) da primeira célula da sequência, soma)
Pista = tuple[str, Celula, int]


def combinacoes_soma(soma: int, tamanho: int) -> list[tuple[int, ...]]:
    """Conjuntos de dígitos distintos 1-9 com `tamanho` elementos somando `soma`."""
    return [c for c in combinations(range(1, 10), tamanho) if sum(c) == soma]


def sequencias(molde: list[str]) -> dict[tuple[str, Celula], list[Celula]]:
    """Sequências de 2+ células brancas, indexadas por (direção, primeira célula)."""
    linhas, colunas = len(molde), len(molde[0]) if molde else 0
    saida: dict[tuple[str, Celula], list[Celula]] = {}
    for r in range(linhas):
        for c in range(colunas):
            if molde[r][c] != ".":
                continue
            if (c == 0 or molde[r][c - 1] == "#") and c + 1 < colunas and molde[r][c + 1] == ".":
                k = c
                while k < colunas and molde[r][k] == ".":
                    k += 1
                saida[("H", (r, c))] = [(r, j) for j in range(c, k)]
            if (r == 0 or molde[r - 1][c] == "#") and r + 1 < linhas and molde[r + 1][c] == ".":
                k = r
                while k < linhas and molde[k][c] == ".":
                    k += 1
                saida[("V", (r, c))] = [(j, c) for j in range(r, k)]
    return saida


def resolver(molde: list[str], pistas: list[Pista]) -> Optional[list[list[int]]]:
    """Grade com dígitos nas células brancas (0 nas pretas), ou None se não houver solução.

    Levanta ValueError se faltar pista para alguma sequência.
    """
    seqs = sequencias(molde)
    somas = {(d, p): s for d, p, s in pistas}
    for chave in seqs:
        if chave not in somas:
            raise ValueError(f"sem pista para a sequência {chave}")
    if any(chave not in seqs for chave in somas):
        raise ValueError("pista aponta para sequência inexistente")
    ordem = list(seqs)
    pertence: dict[Celula, list[tuple[str, Celula]]] = {}
    for chave, cels in seqs.items():
        for c in cels:
            pertence.setdefault(c, []).append(chave)
    valores: dict[Celula, int] = {}

    def possivel(chave: tuple[str, Celula], cel: Celula, v: int) -> bool:
        cels = seqs[chave]
        usados = [valores[c] for c in cels if c in valores]
        if v in usados:
            return False
        restantes = len(cels) - len(usados) - 1
        falta = somas[chave] - sum(usados) - v
        if restantes == 0:
            return falta == 0
        # mínimo/máximo para completar com dígitos distintos ainda livres
        livres = [d for d in range(1, 10) if d not in usados and d != v]
        if len(livres) < restantes:
            return False
        return sum(livres[:restantes]) <= falta <= sum(livres[-restantes:])

    celulas = sorted(pertence, key=lambda c: (-len(pertence[c]), c))

    def busca(i: int) -> bool:
        if i == len(celulas):
            return True
        cel = celulas[i]
        for v in range(1, 10):
            if all(possivel(k, cel, v) for k in pertence[cel]):
                valores[cel] = v
                if busca(i + 1):
                    return True
                del valores[cel]
        return False

    if not busca(0):
        return None
    return [[valores.get((r, c), 0) for c in range(len(molde[0]))] for r in range(len(molde))]


def contar_solucoes(molde: list[str], pistas: list[Pista], limite: int = 2) -> int:
    """Conta soluções até `limite` (para verificar unicidade)."""
    seqs = sequencias(molde)
    somas = {(d, p): s for d, p, s in pistas}
    pertence: dict[Celula, list[tuple[str, Celula]]] = {}
    for chave, cels in seqs.items():
        for c in cels:
            pertence.setdefault(c, []).append(chave)
    celulas = sorted(pertence)
    valores: dict[Celula, int] = {}
    total = 0

    def ok(cel: Celula, v: int) -> bool:
        for chave in pertence[cel]:
            cels = seqs[chave]
            usados = [valores[c] for c in cels if c in valores]
            if v in usados:
                return False
            soma = sum(usados) + v
            if len(usados) + 1 == len(cels):
                if soma != somas[chave]:
                    return False
            elif soma >= somas[chave]:
                return False
        return True

    def busca(i: int) -> None:
        nonlocal total
        if total >= limite:
            return
        if i == len(celulas):
            total += 1
            return
        for v in range(1, 10):
            if ok(celulas[i], v):
                valores[celulas[i]] = v
                busca(i + 1)
                del valores[celulas[i]]

    busca(0)
    return total
