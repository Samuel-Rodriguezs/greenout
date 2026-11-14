"""Operador Laplaciano (segunda derivada) para realce de bordas."""

from img_convolucao import correlacionar, limitar

Imagem = list[list[int]]
Matriz = list[list[float]]

_KERNELS = {
    4: [[0, 1, 0], [1, -4, 1], [0, 1, 0]],
    8: [[1, 1, 1], [1, -8, 1], [1, 1, 1]],
}


def laplaciano(imagem: Imagem, conectividade: int = 4, borda: str = "replicar") -> Matriz:
    """Resposta bruta (pode ser negativa) com vizinhança de 4 ou 8 pixels."""
    if conectividade not in _KERNELS:
        raise ValueError("conectividade deve ser 4 ou 8")
    return correlacionar(imagem, _KERNELS[conectividade], borda)


def bordas_laplaciano(imagem: Imagem, conectividade: int = 4) -> Imagem:
    """Valor absoluto da resposta, limitado a 0..255."""
    return limitar([[abs(v) for v in l] for l in laplaciano(imagem, conectividade)])


def cruzamentos_zero(imagem: Imagem, conectividade: int = 4, limiar: float = 0.0) -> Imagem:
    """Marca com 255 os pixels onde a resposta muda de sinal em relação ao vizinho
    à direita ou abaixo (com variação maior que `limiar`)."""
    r = laplaciano(imagem, conectividade)
    alt, larg = len(r), len(r[0])
    saida = [[0] * larg for _ in range(alt)]
    for y in range(alt):
        for x in range(larg):
            for yy, xx in ((y, x + 1), (y + 1, x)):
                if yy < alt and xx < larg:
                    a, b = r[y][x], r[yy][xx]
                    if a * b < 0 and abs(a - b) > limiar:
                        saida[y][x] = 255
    return saida
