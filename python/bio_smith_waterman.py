"""Alinhamento local de Smith-Waterman com gap linear."""


def alinhar_local(
    a: str, b: str, match: int = 2, mismatch: int = -1, gap: int = -1
) -> tuple[int, str, str, int, int]:
    """Retorna (pontuação, trecho_a, trecho_b, início_a, início_b).

    Os inícios são índices base 0 do trecho alinhado em cada sequência.
    Sem similaridade positiva: (0, '', '', 0, 0).
    """
    n, m = len(a), len(b)
    h = [[0] * (m + 1) for _ in range(n + 1)]
    melhor, pi, pj = 0, 0, 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = match if a[i - 1] == b[j - 1] else mismatch
            h[i][j] = max(0, h[i - 1][j - 1] + s, h[i - 1][j] + gap, h[i][j - 1] + gap)
            if h[i][j] > melhor:
                melhor, pi, pj = h[i][j], i, j
    if melhor == 0:
        return 0, "", "", 0, 0
    ra, rb = [], []
    i, j = pi, pj
    while i > 0 and j > 0 and h[i][j] > 0:
        s = match if a[i - 1] == b[j - 1] else mismatch
        if h[i][j] == h[i - 1][j - 1] + s:
            ra.append(a[i - 1])
            rb.append(b[j - 1])
            i, j = i - 1, j - 1
        elif h[i][j] == h[i - 1][j] + gap:
            ra.append(a[i - 1])
            rb.append("-")
            i -= 1
        else:
            ra.append("-")
            rb.append(b[j - 1])
            j -= 1
    return melhor, "".join(reversed(ra)), "".join(reversed(rb)), i, j
