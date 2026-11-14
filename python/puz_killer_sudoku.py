"""Killer sudoku: sudoku com gaiolas de soma (sem repetição dentro da gaiola); backtracking com MRV."""
from __future__ import annotations

from math import isqrt
from typing import Optional

Celula = tuple[int, int]
Gaiola = tuple[tuple[Celula, ...], int]


def validar_gaiolas(n: int, gaiolas: list[Gaiola]) -> None:
    """As gaiolas devem particionar a grade n x n."""
    vistas: set[Celula] = set()
    for cels, soma in gaiolas:
        if not cels or soma < 0:
            raise ValueError("gaiola inválida")
        for c in cels:
            if not (0 <= c[0] < n and 0 <= c[1] < n):
                raise ValueError(f"célula fora da grade: {c}")
            if c in vistas:
                raise ValueError(f"célula em duas gaiolas: {c}")
            vistas.add(c)
    if len(vistas) != n * n:
        raise ValueError("as gaiolas não cobrem toda a grade")


def resolver(n: int, gaiolas: list[Gaiola],
             dados: Optional[dict[Celula, int]] = None) -> Optional[list[list[int]]]:
    """Resolve um killer sudoku n x n (n quadrado perfeito). None se não houver solução."""
    caixa = isqrt(n)
    if caixa * caixa != n:
        raise ValueError("n deve ser quadrado perfeito")
    validar_gaiolas(n, gaiolas)
    gaiola_de: dict[Celula, int] = {}
    for i, (cels, _) in enumerate(gaiolas):
        for c in cels:
            gaiola_de[c] = i
    grade = [[0] * n for _ in range(n)]
    linhas = [set() for _ in range(n)]
    colunas = [set() for _ in range(n)]
    caixas = [set() for _ in range(n)]
    usados_gaiola: list[set[int]] = [set() for _ in gaiolas]
    soma_gaiola = [0] * len(gaiolas)
    preenchidas_gaiola = [0] * len(gaiolas)

    def caixa_de(r: int, c: int) -> int:
        return r // caixa * caixa + c // caixa

    def candidatos(r: int, c: int) -> list[int]:
        g = gaiola_de[(r, c)]
        cels, alvo = gaiolas[g]
        faltam = len(cels) - preenchidas_gaiola[g]
        res = []
        for v in range(1, n + 1):
            if v in linhas[r] or v in colunas[c] or v in caixas[caixa_de(r, c)] or v in usados_gaiola[g]:
                continue
            restante = alvo - soma_gaiola[g] - v
            if faltam == 1:
                if restante != 0:
                    continue
            else:
                livres = [d for d in range(1, n + 1) if d not in usados_gaiola[g] and d != v]
                k = faltam - 1
                if len(livres) < k or not sum(livres[:k]) <= restante <= sum(livres[-k:]):
                    continue
            res.append(v)
        return res

    def colocar(r: int, c: int, v: int) -> None:
        g = gaiola_de[(r, c)]
        grade[r][c] = v
        linhas[r].add(v)
        colunas[c].add(v)
        caixas[caixa_de(r, c)].add(v)
        usados_gaiola[g].add(v)
        soma_gaiola[g] += v
        preenchidas_gaiola[g] += 1

    def tirar(r: int, c: int) -> None:
        g = gaiola_de[(r, c)]
        v = grade[r][c]
        grade[r][c] = 0
        linhas[r].discard(v)
        colunas[c].discard(v)
        caixas[caixa_de(r, c)].discard(v)
        usados_gaiola[g].discard(v)
        soma_gaiola[g] -= v
        preenchidas_gaiola[g] -= 1

    for (r, c), v in (dados or {}).items():
        if v not in candidatos(r, c):
            return None
        colocar(r, c, v)

    def busca() -> bool:
        melhor, melhores = None, None
        for r in range(n):
            for c in range(n):
                if grade[r][c] == 0:
                    cand = candidatos(r, c)
                    if not cand:
                        return False
                    if melhores is None or len(cand) < len(melhores):
                        melhor, melhores = (r, c), cand
                        if len(cand) == 1:
                            break
            if melhores is not None and len(melhores) == 1:
                break
        if melhor is None:
            return True
        r, c = melhor
        for v in melhores:
            colocar(r, c, v)
            if busca():
                return True
            tirar(r, c)
        return False

    return [linha[:] for linha in grade] if busca() else None


def gaiolas_de_solucao(solucao: list[list[int]], particao: list[list[Celula]]) -> list[Gaiola]:
    """Constrói as gaiolas (com somas) de uma partição e uma solução conhecida."""
    return [(tuple(p), sum(solucao[r][c] for r, c in p)) for p in particao]


def eh_solucao(n: int, grade: list[list[int]], gaiolas: list[Gaiola]) -> bool:
    caixa = isqrt(n)
    alvo = set(range(1, n + 1))
    if any(set(l) != alvo for l in grade) or any({grade[r][c] for r in range(n)} != alvo for c in range(n)):
        return False
    for br in range(0, n, caixa):
        for bc in range(0, n, caixa):
            if {grade[br + i][bc + j] for i in range(caixa) for j in range(caixa)} != alvo:
                return False
    for cels, soma in gaiolas:
        valores = [grade[r][c] for r, c in cels]
        if sum(valores) != soma or len(set(valores)) != len(valores):
            return False
    return True
