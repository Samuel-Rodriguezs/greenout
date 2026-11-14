"""Morfologia matemática: erosão, dilatação, abertura e fechamento.

Funciona em imagens binárias (0/255) e em tons de cinza (mínimo/máximo local).
Pixels fora da imagem não participam da vizinhança.
"""

Imagem = list[list[int]]
Elemento = list[list[int]]


def elemento_quadrado(n: int = 3) -> Elemento:
    if n < 1 or n % 2 == 0:
        raise ValueError("tamanho deve ser ímpar e positivo")
    return [[1] * n for _ in range(n)]


def elemento_cruz() -> Elemento:
    return [[0, 1, 0], [1, 1, 1], [0, 1, 0]]


def _aplicar(imagem: Imagem, elemento: Elemento, funcao) -> Imagem:
    eh, ew = len(elemento), len(elemento[0])
    if eh % 2 == 0 or ew % 2 == 0:
        raise ValueError("elemento estruturante deve ter dimensões ímpares")
    cy, cx = eh // 2, ew // 2
    alt, larg = len(imagem), len(imagem[0])
    saida = []
    for y in range(alt):
        linha = []
        for x in range(larg):
            vizinhos = [
                imagem[y + j - cy][x + i - cx]
                for j in range(eh) for i in range(ew)
                if elemento[j][i] and 0 <= y + j - cy < alt and 0 <= x + i - cx < larg
            ]
            linha.append(funcao(vizinhos))
        saida.append(linha)
    return saida


def erodir(imagem: Imagem, elemento: Elemento | None = None) -> Imagem:
    return _aplicar(imagem, elemento or elemento_quadrado(), min)


def dilatar(imagem: Imagem, elemento: Elemento | None = None) -> Imagem:
    return _aplicar(imagem, elemento or elemento_quadrado(), max)


def abrir(imagem: Imagem, elemento: Elemento | None = None) -> Imagem:
    """Erosão seguida de dilatação: remove objetos menores que o elemento."""
    return dilatar(erodir(imagem, elemento), elemento)


def fechar(imagem: Imagem, elemento: Elemento | None = None) -> Imagem:
    """Dilatação seguida de erosão: preenche buracos menores que o elemento."""
    return erodir(dilatar(imagem, elemento), elemento)


def gradiente_morfologico(imagem: Imagem, elemento: Elemento | None = None) -> Imagem:
    """Dilatação menos erosão: contorno dos objetos."""
    d, e = dilatar(imagem, elemento), erodir(imagem, elemento)
    return [[a - b for a, b in zip(ld, le)] for ld, le in zip(d, e)]
