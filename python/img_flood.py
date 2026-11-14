"""Preenchimento por inundação (flood fill) iterativo."""

Pixel = int | tuple[int, ...]
Imagem = list[list[Pixel]]


def _proximo(a: Pixel, b: Pixel, tolerancia: int) -> bool:
    if isinstance(a, tuple):
        return all(abs(ca - cb) <= tolerancia for ca, cb in zip(a, b))
    return abs(a - b) <= tolerancia


def preencher_regiao(imagem: Imagem, x: int, y: int, novo: Pixel,
                     conectividade: int = 4, tolerancia: int = 0) -> Imagem:
    """Retorna uma cópia em que a região conexa de (x, y) é pintada com `novo`.

    A região contém pixels cuja cor difere da cor semente por no máximo
    `tolerancia` (por canal, em imagens RGB).
    """
    alt, larg = len(imagem), len(imagem[0])
    if not (0 <= y < alt and 0 <= x < larg):
        raise ValueError("ponto semente fora da imagem")
    if conectividade == 4:
        vizinhos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif conectividade == 8:
        vizinhos = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
    else:
        raise ValueError("conectividade deve ser 4 ou 8")
    saida = [list(linha) for linha in imagem]
    alvo = imagem[y][x]
    visitado = [[False] * larg for _ in range(alt)]
    visitado[y][x] = True
    pilha = [(y, x)]
    while pilha:
        cy, cx = pilha.pop()
        saida[cy][cx] = novo
        for dy, dx in vizinhos:
            ny, nx = cy + dy, cx + dx
            if (0 <= ny < alt and 0 <= nx < larg and not visitado[ny][nx]
                    and _proximo(imagem[ny][nx], alvo, tolerancia)):
                visitado[ny][nx] = True
                pilha.append((ny, nx))
    return saida
