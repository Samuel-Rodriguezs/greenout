"""Validador de tabuleiro de Sudoku 9x9."""


def sudoku_valido(tabuleiro: list[list[int]]) -> bool:
    """Verifica se o tabuleiro (0 = vazio) não viola linhas, colunas ou blocos 3x3."""
    if len(tabuleiro) != 9 or any(len(linha) != 9 for linha in tabuleiro):
        raise ValueError("tabuleiro deve ser 9x9")
    linhas = [set() for _ in range(9)]
    colunas = [set() for _ in range(9)]
    blocos = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = tabuleiro[r][c]
            if not isinstance(v, int) or not 0 <= v <= 9:
                raise ValueError(f"valor inválido: {v!r}")
            if v == 0:
                continue
            b = (r // 3) * 3 + c // 3
            if v in linhas[r] or v in colunas[c] or v in blocos[b]:
                return False
            linhas[r].add(v)
            colunas[c].add(v)
            blocos[b].add(v)
    return True
