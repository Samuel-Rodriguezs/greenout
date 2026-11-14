"""Rotulagem de componentes conexos em imagens binárias."""

from collections import deque

Imagem = list[list[int]]


def rotular(imagem: Imagem, conectividade: int = 4, fundo: int = 0) -> tuple[Imagem, int]:
    """Retorna (matriz de rótulos, quantidade de componentes).

    Pixels iguais a `fundo` recebem 0; os componentes são numerados de 1 em
    diante pela ordem de varredura (linha a linha).
    """
    if conectividade == 4:
        vizinhos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif conectividade == 8:
        vizinhos = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
    else:
        raise ValueError("conectividade deve ser 4 ou 8")
    alt, larg = len(imagem), len(imagem[0])
    rotulos = [[0] * larg for _ in range(alt)]
    n = 0
    for y in range(alt):
        for x in range(larg):
            if imagem[y][x] == fundo or rotulos[y][x]:
                continue
            n += 1
            rotulos[y][x] = n
            fila = deque([(y, x)])
            while fila:
                cy, cx = fila.popleft()
                for dy, dx in vizinhos:
                    ny, nx = cy + dy, cx + dx
                    if (0 <= ny < alt and 0 <= nx < larg
                            and imagem[ny][nx] != fundo and not rotulos[ny][nx]):
                        rotulos[ny][nx] = n
                        fila.append((ny, nx))
    return rotulos, n


def areas(rotulos: Imagem) -> dict[int, int]:
    """Número de pixels de cada rótulo (exceto o fundo)."""
    contagem: dict[int, int] = {}
    for linha in rotulos:
        for r in linha:
            if r:
                contagem[r] = contagem.get(r, 0) + 1
    return contagem


def caixas_delimitadoras(rotulos: Imagem) -> dict[int, tuple[int, int, int, int]]:
    """Retângulo (x_min, y_min, x_max, y_max) de cada componente."""
    caixas: dict[int, tuple[int, int, int, int]] = {}
    for y, linha in enumerate(rotulos):
        for x, r in enumerate(linha):
            if r:
                x0, y0, x1, y1 = caixas.get(r, (x, y, x, y))
                caixas[r] = (min(x0, x), min(y0, y), max(x1, x), max(y1, y))
    return caixas
