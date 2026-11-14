"""Maior subsequência comum (LCS) entre duas sequências de texto."""


def maior_subsequencia_comum(a: str, b: str) -> str:
    """Retorna uma maior subsequência comum entre `a` e `b`."""
    n, m = len(a), len(b)
    tab = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                tab[i][j] = tab[i + 1][j + 1] + 1
            else:
                tab[i][j] = max(tab[i + 1][j], tab[i][j + 1])
    resultado = []
    i = j = 0
    while i < n and j < m:
        if a[i] == b[j]:
            resultado.append(a[i])
            i += 1
            j += 1
        elif tab[i + 1][j] >= tab[i][j + 1]:
            i += 1
        else:
            j += 1
    return "".join(resultado)
