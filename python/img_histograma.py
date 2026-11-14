"""Histograma, histograma acumulado e equalização de histograma."""

Imagem = list[list[int]]


def histograma(imagem: Imagem, niveis: int = 256) -> list[int]:
    hist = [0] * niveis
    for linha in imagem:
        for v in linha:
            if not 0 <= v < niveis:
                raise ValueError(f"valor {v} fora de 0..{niveis - 1}")
            hist[v] += 1
    return hist


def histograma_acumulado(hist: list[int]) -> list[int]:
    acc = []
    soma = 0
    for c in hist:
        soma += c
        acc.append(soma)
    return acc


def equalizar(imagem: Imagem, niveis: int = 256) -> Imagem:
    """Equalização clássica: v' = round((cdf(v) - cdf_min) / (N - cdf_min) * (L - 1))."""
    cdf = histograma_acumulado(histograma(imagem, niveis))
    total = cdf[-1]
    if total == 0:
        raise ValueError("imagem vazia")
    cdf_min = next(c for c in cdf if c > 0)
    if cdf_min == total:  # imagem uniforme: nada a equalizar
        return [list(linha) for linha in imagem]
    escala = (niveis - 1) / (total - cdf_min)
    return [[round((cdf[v] - cdf_min) * escala) for v in linha] for linha in imagem]
