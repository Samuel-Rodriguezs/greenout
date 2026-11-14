"""Filtro de mediana, eficaz contra ruído sal e pimenta."""

from img_convolucao import indice_borda

Imagem = list[list[int]]
RGB = tuple[int, int, int]


def _mediana(valores: list[int]) -> int:
    ordenados = sorted(valores)
    n = len(ordenados)
    if n % 2:
        return ordenados[n // 2]
    return round((ordenados[n // 2 - 1] + ordenados[n // 2]) / 2)


def filtro_mediana(imagem: Imagem, raio: int = 1, borda: str = "replicar") -> Imagem:
    """Substitui cada pixel pela mediana da janela (2r+1)x(2r+1).

    Com borda "zero", pixels fora da imagem entram na janela como 0.
    """
    if raio < 1:
        raise ValueError("raio deve ser >= 1")
    alt, larg = len(imagem), len(imagem[0])
    saida = []
    for y in range(alt):
        linha = []
        for x in range(larg):
            janela = []
            for dy in range(-raio, raio + 1):
                yy = indice_borda(y + dy, alt, borda)
                for dx in range(-raio, raio + 1):
                    xx = indice_borda(x + dx, larg, borda)
                    janela.append(0 if yy is None or xx is None else imagem[yy][xx])
            linha.append(_mediana(janela))
        saida.append(linha)
    return saida


def filtro_mediana_rgb(imagem: list[list[RGB]], raio: int = 1,
                       borda: str = "replicar") -> list[list[RGB]]:
    """Aplica a mediana separadamente em cada canal."""
    canais = [filtro_mediana([[p[c] for p in linha] for linha in imagem], raio, borda)
              for c in range(3)]
    return [[(canais[0][y][x], canais[1][y][x], canais[2][y][x])
             for x in range(len(imagem[0]))] for y in range(len(imagem))]
