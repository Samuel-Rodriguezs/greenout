"""Recorte, colagem e preenchimento (de regiões e de bordas) em matrizes de pixels."""

from typing import Any

Matriz = list[list[Any]]


def recortar(imagem: Matriz, x: int, y: int, largura: int, altura: int) -> Matriz:
    """Sub-imagem com canto superior esquerdo em (x, y). Deve caber na imagem."""
    if largura <= 0 or altura <= 0:
        raise ValueError("largura e altura devem ser positivas")
    if x < 0 or y < 0 or y + altura > len(imagem) or x + largura > len(imagem[0]):
        raise ValueError("recorte fora dos limites da imagem")
    return [linha[x:x + largura] for linha in imagem[y:y + altura]]


def preencher_retangulo(imagem: Matriz, x: int, y: int, largura: int, altura: int,
                        valor: Any) -> Matriz:
    """Nova imagem com o retângulo pintado; a parte fora da imagem é ignorada."""
    saida = [list(linha) for linha in imagem]
    for yy in range(max(y, 0), min(y + altura, len(imagem))):
        for xx in range(max(x, 0), min(x + largura, len(imagem[0]))):
            saida[yy][xx] = valor
    return saida


def adicionar_borda(imagem: Matriz, topo: int, base: int, esquerda: int, direita: int,
                    valor: Any = 0) -> Matriz:
    """Acrescenta margens preenchidas com `valor`."""
    if min(topo, base, esquerda, direita) < 0:
        raise ValueError("margens não podem ser negativas")
    larg = len(imagem[0]) + esquerda + direita
    vazia = [valor] * larg
    return ([list(vazia) for _ in range(topo)]
            + [[valor] * esquerda + list(l) + [valor] * direita for l in imagem]
            + [list(vazia) for _ in range(base)])


def colar(destino: Matriz, origem: Matriz, x: int, y: int) -> Matriz:
    """Nova imagem com `origem` colada em (x, y), cortada se passar dos limites."""
    saida = [list(linha) for linha in destino]
    for j, linha in enumerate(origem):
        for i, v in enumerate(linha):
            if 0 <= y + j < len(destino) and 0 <= x + i < len(destino[0]):
                saida[y + j][x + i] = v
    return saida
