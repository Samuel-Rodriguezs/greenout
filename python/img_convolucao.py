"""Convolução e correlação 2D com vários tratamentos de borda."""

Matriz = list[list[float]]
Imagem = list[list[int]]

BORDAS = ("replicar", "espelhar", "circular", "zero")


def indice_borda(i: int, n: int, borda: str) -> int | None:
    """Mapeia um índice possivelmente fora de [0, n) para um índice válido.

    Retorna None quando a borda é "zero" (o pixel contribui com 0).
    """
    if 0 <= i < n:
        return i
    if borda == "replicar":
        return 0 if i < 0 else n - 1
    if borda == "circular":
        return i % n
    if borda == "espelhar":  # reflexão sem repetir o pixel da borda
        if n == 1:
            return 0
        periodo = 2 * (n - 1)
        i %= periodo
        return i if i < n else periodo - i
    if borda == "zero":
        return None
    raise ValueError(f"borda desconhecida: {borda}")


def correlacionar(imagem: Matriz, kernel: Matriz, borda: str = "replicar",
                  divisor: float = 1.0) -> Matriz:
    """Correlação: o kernel é aplicado sem inversão. Retorna valores brutos (float)."""
    kh, kw = len(kernel), len(kernel[0])
    if kh % 2 == 0 or kw % 2 == 0 or any(len(r) != kw for r in kernel):
        raise ValueError("kernel deve ter dimensões ímpares e retangulares")
    if divisor == 0:
        raise ValueError("divisor não pode ser zero")
    alt, larg = len(imagem), len(imagem[0])
    cy, cx = kh // 2, kw // 2
    saida: Matriz = []
    for y in range(alt):
        linha = []
        for x in range(larg):
            soma = 0.0
            for j in range(kh):
                yy = indice_borda(y + j - cy, alt, borda)
                if yy is None:
                    continue
                for i in range(kw):
                    xx = indice_borda(x + i - cx, larg, borda)
                    if xx is not None:
                        soma += kernel[j][i] * imagem[yy][xx]
            linha.append(soma / divisor)
        saida.append(linha)
    return saida


def convolver(imagem: Matriz, kernel: Matriz, borda: str = "replicar",
              divisor: float = 1.0) -> Matriz:
    """Convolução verdadeira: o kernel é girado 180 graus antes da aplicação."""
    girado = [linha[::-1] for linha in kernel[::-1]]
    return correlacionar(imagem, girado, borda, divisor)


def limitar(imagem: Matriz) -> Imagem:
    """Arredonda e restringe os valores à faixa 0..255."""
    return [[max(0, min(255, round(v))) for v in linha] for linha in imagem]
