"""KenKen: quadrado latino n x n com gaiolas aritméticas (+, -, *, /, = ); solver por backtracking."""
from __future__ import annotations

from itertools import product
from math import prod
from typing import Optional

Celula = tuple[int, int]
# (células, operador, alvo); '-' e '/' exigem exatamente 2 células; '=' exige 1.
Gaiola = tuple[tuple[Celula, ...], str, int]


def satisfaz(valores: list[int], op: str, alvo: int) -> bool:
    if op == "=":
        return len(valores) == 1 and valores[0] == alvo
    if op == "+":
        return sum(valores) == alvo
    if op == "*":
        return prod(valores) == alvo
    if op == "-":
        return len(valores) == 2 and abs(valores[0] - valores[1]) == alvo
    if op == "/":
        a, b = sorted(valores)
        return len(valores) == 2 and b % a == 0 and b // a == alvo
    raise ValueError(f"operador inválido: {op}")


def _valida_entrada(n: int, gaiolas: list[Gaiola]) -> None:
    vistas: set[Celula] = set()
    for cels, op, alvo in gaiolas:
        if op not in "=+-*/" or len(op) != 1:
            raise ValueError(f"operador inválido: {op}")
        if (op == "=" and len(cels) != 1) or (op in "-/" and len(cels) != 2):
            raise ValueError(f"tamanho de gaiola incompatível com '{op}'")
        for c in cels:
            if not (0 <= c[0] < n and 0 <= c[1] < n) or c in vistas:
                raise ValueError(f"célula inválida ou repetida: {c}")
            vistas.add(c)
    if len(vistas) != n * n:
        raise ValueError("as gaiolas não cobrem toda a grade")


def _tuplas_possiveis(n: int, cels: tuple[Celula, ...], op: str, alvo: int) -> list[tuple[int, ...]]:
    """Todas as atribuições da gaiola que satisfazem a conta e não repetem valor em linha/coluna."""
    saida = []
    for t in product(range(1, n + 1), repeat=len(cels)):
        if not satisfaz(list(t), op, alvo):
            continue
        ok = True
        for i in range(len(cels)):
            for j in range(i + 1, len(cels)):
                if t[i] == t[j] and (cels[i][0] == cels[j][0] or cels[i][1] == cels[j][1]):
                    ok = False
        if ok:
            saida.append(t)
    return saida


def resolver(n: int, gaiolas: list[Gaiola]) -> Optional[list[list[int]]]:
    """Retorna a grade resolvida ou None. Cada linha e coluna contém 1..n sem repetição."""
    _valida_entrada(n, gaiolas)
    opcoes = [_tuplas_possiveis(n, cels, op, alvo) for cels, op, alvo in gaiolas]
    if any(not o for o in opcoes):
        return None
    ordem = sorted(range(len(gaiolas)), key=lambda i: len(opcoes[i]))
    grade = [[0] * n for _ in range(n)]
    linhas = [set() for _ in range(n)]
    colunas = [set() for _ in range(n)]

    def busca(k: int) -> bool:
        if k == len(ordem):
            return True
        i = ordem[k]
        cels = gaiolas[i][0]
        for t in opcoes[i]:
            if any(v in linhas[r] or v in colunas[c] for (r, c), v in zip(cels, t)):
                continue
            for (r, c), v in zip(cels, t):
                grade[r][c] = v
                linhas[r].add(v)
                colunas[c].add(v)
            if busca(k + 1):
                return True
            for (r, c), v in zip(cels, t):
                grade[r][c] = 0
                linhas[r].discard(v)
                colunas[c].discard(v)
        return False

    return [l[:] for l in grade] if busca(0) else None


def contar_solucoes(n: int, gaiolas: list[Gaiola], limite: int = 2) -> int:
    """Número de soluções (até `limite`)."""
    _valida_entrada(n, gaiolas)
    opcoes = [_tuplas_possiveis(n, cels, op, alvo) for cels, op, alvo in gaiolas]
    if any(not o for o in opcoes):
        return 0
    ordem = sorted(range(len(gaiolas)), key=lambda i: len(opcoes[i]))
    linhas = [set() for _ in range(n)]
    colunas = [set() for _ in range(n)]
    total = 0

    def busca(k: int) -> None:
        nonlocal total
        if total >= limite:
            return
        if k == len(ordem):
            total += 1
            return
        cels = gaiolas[ordem[k]][0]
        for t in opcoes[ordem[k]]:
            if any(v in linhas[r] or v in colunas[c] for (r, c), v in zip(cels, t)):
                continue
            for (r, c), v in zip(cels, t):
                linhas[r].add(v)
                colunas[c].add(v)
            busca(k + 1)
            for (r, c), v in zip(cels, t):
                linhas[r].discard(v)
                colunas[c].discard(v)

    busca(0)
    return total
