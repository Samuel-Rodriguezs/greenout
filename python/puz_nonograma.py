"""Nonograma: solver por propagação de linhas com retrocesso quando necessário."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

# Células: 1 = preenchida, 0 = vazia, -1 = desconhecida
DESCONHECIDA = -1


def arranjos(pistas: tuple[int, ...], tamanho: int, linha: tuple[int, ...]) -> list[tuple[int, ...]]:
    """Todos os preenchimentos de uma linha compatíveis com as pistas e células conhecidas."""

    @lru_cache(maxsize=None)
    def gerar(i: int, pos: int) -> tuple[tuple[int, ...], ...]:
        if i == len(pistas):
            resto = linha[pos:]
            return ((0,) * (tamanho - pos),) if 1 not in resto else ()
        bloco = pistas[i]
        minimo = sum(pistas[i + 1:]) + (len(pistas) - i - 1)
        saida = []
        for ini in range(pos, tamanho - bloco - minimo + 1):
            prefixo = (0,) * (ini - pos) + (1,) * bloco
            fim = ini + bloco
            if fim < tamanho:
                prefixo += (0,)
                fim += 1
            trecho = linha[pos:fim]
            if any(a != DESCONHECIDA and a != b for a, b in zip(trecho, prefixo)):
                continue
            for cauda in gerar(i + 1, fim):
                saida.append(prefixo + cauda)
        return tuple(saida)

    return list(gerar(0, 0))


def _propagar(grade: list[list[int]], linhas, colunas) -> bool:
    """Propaga até estabilizar; False se houver contradição."""
    n_l, n_c = len(linhas), len(colunas)
    mudou = True
    while mudou:
        mudou = False
        for eh_linha, pistas_todas, qtd, tam in ((True, linhas, n_l, n_c), (False, colunas, n_c, n_l)):
            for k in range(qtd):
                atual = tuple(grade[k]) if eh_linha else tuple(grade[r][k] for r in range(n_l))
                opcoes = arranjos(tuple(pistas_todas[k]), tam, atual)
                if not opcoes:
                    return False
                for j in range(tam):
                    vals = {o[j] for o in opcoes}
                    if len(vals) == 1 and atual[j] == DESCONHECIDA:
                        v = vals.pop()
                        if eh_linha:
                            grade[k][j] = v
                        else:
                            grade[j][k] = v
                        mudou = True
    return True


def resolver(linhas: list[list[int]], colunas: list[list[int]]) -> Optional[list[list[int]]]:
    """Retorna uma solução (grade de 0/1) ou None se não existir."""
    if sum(map(sum, linhas)) != sum(map(sum, colunas)):
        return None
    grade = [[DESCONHECIDA] * len(colunas) for _ in linhas]

    def buscar(g: list[list[int]]) -> Optional[list[list[int]]]:
        if not _propagar(g, linhas, colunas):
            return None
        for r, lin in enumerate(g):
            for c, v in enumerate(lin):
                if v == DESCONHECIDA:
                    for tentativa in (1, 0):
                        copia = [l[:] for l in g]
                        copia[r][c] = tentativa
                        res = buscar(copia)
                        if res:
                            return res
                    return None
        return g

    return buscar(grade)


def contar_solucoes(linhas: list[list[int]], colunas: list[list[int]], limite: int = 2) -> int:
    """Conta soluções até um limite (útil para checar unicidade)."""
    total = 0

    def buscar(g: list[list[int]]) -> None:
        nonlocal total
        if total >= limite or not _propagar(g, linhas, colunas):
            return
        for r, lin in enumerate(g):
            for c, v in enumerate(lin):
                if v == DESCONHECIDA:
                    for t in (1, 0):
                        copia = [l[:] for l in g]
                        copia[r][c] = t
                        buscar(copia)
                    return
        total += 1

    buscar([[DESCONHECIDA] * len(colunas) for _ in linhas])
    return total


def pistas_de(grade: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    def da_linha(lin):
        blocos, cont = [], 0
        for v in lin:
            if v == 1:
                cont += 1
            elif cont:
                blocos.append(cont)
                cont = 0
        if cont:
            blocos.append(cont)
        return blocos

    return [da_linha(l) for l in grade], [da_linha(c) for c in zip(*grade)]
