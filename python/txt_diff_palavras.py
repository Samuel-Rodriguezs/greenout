"""Diff de palavras baseado na maior subsequência comum (LCS)."""


def diff_palavras(antes: str, depois: str) -> list[tuple[str, str]]:
    """Lista de ('=' | '-' | '+', palavra) transformando `antes` em `depois`."""
    a, b = antes.split(), depois.split()
    n, m = len(a), len(b)
    lcs = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                lcs[i][j] = lcs[i + 1][j + 1] + 1
            else:
                lcs[i][j] = max(lcs[i + 1][j], lcs[i][j + 1])
    saida: list[tuple[str, str]] = []
    i = j = 0
    while i < n and j < m:
        if a[i] == b[j]:
            saida.append(("=", a[i]))
            i += 1
            j += 1
        elif lcs[i + 1][j] >= lcs[i][j + 1]:
            saida.append(("-", a[i]))
            i += 1
        else:
            saida.append(("+", b[j]))
            j += 1
    saida.extend(("-", w) for w in a[i:])
    saida.extend(("+", w) for w in b[j:])
    return saida


def formatar(diff: list[tuple[str, str]]) -> str:
    """Renderiza o diff como texto: [-removida-] {+adicionada+}."""
    partes = []
    for op, w in diff:
        partes.append(w if op == "=" else f"[-{w}-]" if op == "-" else f"{{+{w}+}}")
    return " ".join(partes)


def similaridade(antes: str, depois: str) -> float:
    """Razão 2*iguais/(total de palavras); 1.0 quando ambos vazios."""
    d = diff_palavras(antes, depois)
    iguais = sum(1 for op, _ in d if op == "=")
    total = len(antes.split()) + len(depois.split())
    return 1.0 if total == 0 else 2 * iguais / total
