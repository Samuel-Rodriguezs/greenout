"""Quantização de cores: níveis uniformes por canal e paleta por corte mediano."""

RGB = tuple[int, int, int]
Imagem = list[list[RGB]]


def quantizar_uniforme(imagem: Imagem, bits: int) -> Imagem:
    """Mantém `bits` bits por canal, reespalhando os níveis em 0..255."""
    if not 1 <= bits <= 8:
        raise ValueError("bits deve estar entre 1 e 8")
    maximo = (1 << bits) - 1
    return [[tuple(((c >> (8 - bits)) * 255 + maximo // 2) // maximo for c in p)
             for p in linha] for linha in imagem]


def paleta_corte_mediano(imagem: Imagem, k: int) -> list[RGB]:
    """Gera até `k` cores pelo algoritmo de corte mediano (median cut).

    A caixa com mais pixels é dividida na mediana do canal de maior amplitude;
    cada caixa final contribui com a média de suas cores. Saída ordenada.
    """
    if k < 1:
        raise ValueError("k deve ser >= 1")
    caixas = [[p for linha in imagem for p in linha]]
    while len(caixas) < k:
        candidatas = [c for c in caixas if len(set(c)) > 1]
        if not candidatas:
            break
        caixa = max(candidatas, key=len)
        canal = max(range(3), key=lambda i: max(p[i] for p in caixa) - min(p[i] for p in caixa))
        ordenada = sorted(caixa, key=lambda p: (p[canal], p))
        meio = len(ordenada) // 2
        caixas.remove(caixa)
        caixas.extend([ordenada[:meio], ordenada[meio:]])
    paleta = [tuple(round(sum(p[i] for p in c) / len(c)) for i in range(3)) for c in caixas]
    return sorted(set(paleta))


def cor_mais_proxima(pixel: RGB, paleta: list[RGB]) -> RGB:
    """Cor da paleta com menor distância euclidiana; empate fica com a primeira."""
    return min(paleta, key=lambda c: sum((a - b) ** 2 for a, b in zip(pixel, c)))


def aplicar_paleta(imagem: Imagem, paleta: list[RGB]) -> Imagem:
    if not paleta:
        raise ValueError("paleta vazia")
    return [[cor_mais_proxima(p, paleta) for p in linha] for linha in imagem]
