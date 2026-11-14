"""Dithering de Floyd-Steinberg (difusão de erro) para poucos níveis de cinza."""

Imagem = list[list[int]]


def floyd_steinberg(imagem: Imagem, niveis: int = 2) -> Imagem:
    """Reduz a imagem a `niveis` tons uniformes entre 0 e 255 difundindo o erro.

    O erro de cada pixel é distribuído para a direita (7/16) e para a linha
    seguinte: esquerda (3/16), abaixo (5/16) e direita (1/16).
    """
    if niveis < 2 or niveis > 256:
        raise ValueError("niveis deve estar entre 2 e 256")
    alt, larg = len(imagem), len(imagem[0])
    trabalho = [[float(v) for v in linha] for linha in imagem]
    passo = 255 / (niveis - 1)
    saida = [[0] * larg for _ in range(alt)]
    for y in range(alt):
        for x in range(larg):
            antigo = trabalho[y][x]
            indice = max(0, min(niveis - 1, round(antigo / passo)))
            novo = round(indice * passo)
            saida[y][x] = novo
            erro = antigo - novo
            for dy, dx, peso in ((0, 1, 7), (1, -1, 3), (1, 0, 5), (1, 1, 1)):
                yy, xx = y + dy, x + dx
                if yy < alt and 0 <= xx < larg:
                    trabalho[yy][xx] += erro * peso / 16
    return saida
