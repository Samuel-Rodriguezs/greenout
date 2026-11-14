"""Montagem gulosa de fragmentos por sobreposição."""


def sobreposicao(a: str, b: str, minimo: int = 1) -> int:
    """Maior sufixo de ``a`` que é prefixo de ``b`` (0 se menor que ``minimo``)."""
    for k in range(min(len(a), len(b)), max(minimo, 1) - 1, -1):
        if a.endswith(b[:k]):
            return k
    return 0


def montar(fragmentos: list[str], minimo: int = 3) -> list[str]:
    """Funde repetidamente o par de maior sobreposição; devolve os contigs.

    Fragmentos contidos em outros são descartados. A saída vem ordenada.
    """
    fr = list(dict.fromkeys(f for f in fragmentos if f))
    fr = [f for f in fr if not any(f != g and f in g for g in fr)]
    while len(fr) > 1:
        melhor = (0, -1, -1)
        for i, a in enumerate(fr):
            for j, b in enumerate(fr):
                if i != j:
                    k = sobreposicao(a, b, minimo)
                    if k > melhor[0]:
                        melhor = (k, i, j)
        k, i, j = melhor
        if k == 0:
            break
        fundido = fr[i] + fr[j][k:]
        fr = [f for x, f in enumerate(fr) if x not in (i, j)] + [fundido]
    return sorted(fr)
