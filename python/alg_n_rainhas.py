"""Problema das N rainhas com backtracking."""


def resolver_n_rainhas(n: int) -> list[list[int]]:
    """Todas as soluções; cada solução lista a coluna da rainha em cada linha."""
    if n < 0:
        raise ValueError("n não pode ser negativo")
    solucoes: list[list[int]] = []
    colunas: set[int] = set()
    diag1: set[int] = set()
    diag2: set[int] = set()
    atual: list[int] = []

    def colocar(linha: int) -> None:
        if linha == n:
            solucoes.append(atual.copy())
            return
        for c in range(n):
            if c in colunas or linha - c in diag1 or linha + c in diag2:
                continue
            colunas.add(c)
            diag1.add(linha - c)
            diag2.add(linha + c)
            atual.append(c)
            colocar(linha + 1)
            atual.pop()
            colunas.remove(c)
            diag1.remove(linha - c)
            diag2.remove(linha + c)

    colocar(0)
    return solucoes
