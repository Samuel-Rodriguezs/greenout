"""Árvore filogenética por UPGMA, em formato Newick."""


def upgma(nomes: list[str], d: list[list[float]]) -> str:
    """Constrói a árvore a partir de uma matriz de distâncias simétrica."""
    n = len(nomes)
    if n == 0 or len(d) != n or any(len(l) != n for l in d):
        raise ValueError("matriz incompatível com os nomes")
    # cluster: (newick, altura, tamanho)
    cl = {i: (nomes[i], 0.0, 1) for i in range(n)}
    dist = {(i, j): float(d[i][j]) for i in range(n) for j in range(i + 1, n)}
    prox = n
    while len(cl) > 1:
        (i, j), dij = min(dist.items(), key=lambda kv: (kv[1], kv[0]))
        ni, hi, si = cl.pop(i)
        nj, hj, sj = cl.pop(j)
        h = dij / 2
        novo = (f"({ni}:{_f(h - hi)},{nj}:{_f(h - hj)})", h, si + sj)
        dist.pop((i, j))
        for k in cl:
            dik = dist.pop((min(i, k), max(i, k)))
            djk = dist.pop((min(j, k), max(j, k)))
            dist[(k, prox)] = (dik * si + djk * sj) / (si + sj)
        cl[prox] = novo
        prox += 1
    return next(iter(cl.values()))[0] + ";"


def _f(x: float) -> str:
    return f"{x:g}"
