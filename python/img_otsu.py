"""Limiar de Otsu: maximiza a variância entre as classes fundo/objeto."""

Imagem = list[list[int]]


def limiar_otsu(imagem: Imagem) -> int:
    """Retorna o menor t tal que fundo = pixels <= t maximiza a variância entre classes."""
    hist = [0] * 256
    for linha in imagem:
        for v in linha:
            hist[v] += 1
    total = sum(hist)
    if total == 0:
        raise ValueError("imagem vazia")
    soma_total = sum(i * c for i, c in enumerate(hist))
    peso_fundo = 0
    soma_fundo = 0
    melhor_var = -1.0
    melhor_t = 0
    for t in range(256):
        peso_fundo += hist[t]
        soma_fundo += t * hist[t]
        peso_objeto = total - peso_fundo
        if peso_fundo == 0 or peso_objeto == 0:
            continue
        media_f = soma_fundo / peso_fundo
        media_o = (soma_total - soma_fundo) / peso_objeto
        var = peso_fundo * peso_objeto * (media_f - media_o) ** 2
        if var > melhor_var:
            melhor_var = var
            melhor_t = t
    return melhor_t


def binarizar_otsu(imagem: Imagem) -> Imagem:
    """Pixels acima do limiar de Otsu viram 255; os demais, 0."""
    t = limiar_otsu(imagem)
    return [[255 if v > t else 0 for v in linha] for linha in imagem]
