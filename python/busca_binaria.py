def busca_binaria(lista, alvo):
    """Retorna o índice de alvo em lista ordenada, ou -1."""
    lo, hi = 0, len(lista) - 1
    while lo <= hi:
        meio = (lo + hi) // 2
        if lista[meio] == alvo:
            return meio
        if lista[meio] < alvo:
            lo = meio + 1
        else:
            hi = meio - 1
    return -1
