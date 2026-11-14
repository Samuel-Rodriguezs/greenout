"""Problema das ilhas: contagem, maior área e flood fill em grade."""

from __future__ import annotations


def _vizinhos(l: int, c: int, linhas: int, colunas: int, diagonal: bool):
    passos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        passos += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dl, dc in passos:
        nl, nc = l + dl, c + dc
        if 0 <= nl < linhas and 0 <= nc < colunas:
            yield nl, nc


def _areas(grade: list[list[int]], diagonal: bool) -> list[int]:
    linhas = len(grade)
    colunas = len(grade[0]) if linhas else 0
    visto = [[False] * colunas for _ in range(linhas)]
    areas: list[int] = []
    for i in range(linhas):
        for j in range(colunas):
            if grade[i][j] != 1 or visto[i][j]:
                continue
            visto[i][j] = True
            pilha = [(i, j)]
            area = 0
            while pilha:
                l, c = pilha.pop()
                area += 1
                for nl, nc in _vizinhos(l, c, linhas, colunas, diagonal):
                    if grade[nl][nc] == 1 and not visto[nl][nc]:
                        visto[nl][nc] = True
                        pilha.append((nl, nc))
            areas.append(area)
    return areas


def contar_ilhas(grade: list[list[int]], diagonal: bool = False) -> int:
    return len(_areas(grade, diagonal))


def maior_ilha(grade: list[list[int]], diagonal: bool = False) -> int:
    return max(_areas(grade, diagonal), default=0)


def flood_fill(imagem: list[list[int]], l: int, c: int, nova_cor: int) -> list[list[int]]:
    """Retorna cópia da imagem com a região 4-conexa de (l, c) pintada de nova_cor."""
    if not (0 <= l < len(imagem) and 0 <= c < len(imagem[0])):
        raise IndexError("ponto fora da imagem")
    res = [linha[:] for linha in imagem]
    original = res[l][c]
    if original == nova_cor:
        return res
    pilha = [(l, c)]
    res[l][c] = nova_cor
    while pilha:
        x, y = pilha.pop()
        for nx, ny in _vizinhos(x, y, len(res), len(res[0]), False):
            if res[nx][ny] == original:
                res[nx][ny] = nova_cor
                pilha.append((nx, ny))
    return res
