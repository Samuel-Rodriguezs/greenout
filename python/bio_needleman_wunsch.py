"""Alinhamento global de Needleman-Wunsch com gap linear."""


def alinhar(
    a: str, b: str, match: int = 1, mismatch: int = -1, gap: int = -1
) -> tuple[int, str, str]:
    """Retorna (pontuação, a_alinhada, b_alinhada); '-' marca gaps.

    No traceback, empates preferem diagonal, depois gap em b, depois gap em a.
    """
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        f[i][0] = i * gap
    for j in range(1, m + 1):
        f[0][j] = j * gap
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = match if a[i - 1] == b[j - 1] else mismatch
            f[i][j] = max(f[i - 1][j - 1] + s, f[i - 1][j] + gap, f[i][j - 1] + gap)
    ra, rb = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            s = match if a[i - 1] == b[j - 1] else mismatch
            if f[i][j] == f[i - 1][j - 1] + s:
                ra.append(a[i - 1])
                rb.append(b[j - 1])
                i, j = i - 1, j - 1
                continue
        if i > 0 and f[i][j] == f[i - 1][j] + gap:
            ra.append(a[i - 1])
            rb.append("-")
            i -= 1
        else:
            ra.append("-")
            rb.append(b[j - 1])
            j -= 1
    return f[n][m], "".join(reversed(ra)), "".join(reversed(rb))


def identidade(al_a: str, al_b: str) -> float:
    """Fração de colunas idênticas (sem gaps) no alinhamento."""
    if len(al_a) != len(al_b):
        raise ValueError("alinhamento inconsistente")
    if not al_a:
        return 0.0
    return sum(x == y and x != "-" for x, y in zip(al_a, al_b)) / len(al_a)
