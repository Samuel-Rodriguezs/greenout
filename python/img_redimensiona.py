"""Redimensionamento por vizinho mais próximo e interpolação bilinear.

Aceita imagens de cinza (inteiros) ou RGB (tuplas de inteiros).
"""

Pixel = int | tuple[int, ...]
Imagem = list[list[Pixel]]


def _validar(nova_larg: int, nova_alt: int) -> None:
    if nova_larg < 1 or nova_alt < 1:
        raise ValueError("dimensões devem ser positivas")


def vizinho_mais_proximo(imagem: Imagem, nova_larg: int, nova_alt: int) -> Imagem:
    _validar(nova_larg, nova_alt)
    alt, larg = len(imagem), len(imagem[0])
    return [[imagem[y * alt // nova_alt][x * larg // nova_larg] for x in range(nova_larg)]
            for y in range(nova_alt)]


def _mistura(a: Pixel, b: Pixel, t: float) -> float | tuple[float, ...]:
    if isinstance(a, tuple):
        return tuple(ca + (cb - ca) * t for ca, cb in zip(a, b))
    return a + (b - a) * t


def _arredondar(p: float | tuple[float, ...]) -> Pixel:
    if isinstance(p, tuple):
        return tuple(round(c) for c in p)
    return round(p)


def _origem(i: int, novo: int, antigo: int) -> tuple[int, int, float]:
    """Alinha os centros dos pixels; devolve (indice0, indice1, peso de indice1)."""
    pos = (i + 0.5) * antigo / novo - 0.5
    pos = max(0.0, min(antigo - 1.0, pos))
    i0 = int(pos)
    return i0, min(i0 + 1, antigo - 1), pos - i0


def bilinear(imagem: Imagem, nova_larg: int, nova_alt: int) -> Imagem:
    _validar(nova_larg, nova_alt)
    alt, larg = len(imagem), len(imagem[0])
    saida: Imagem = []
    for y in range(nova_alt):
        y0, y1, ty = _origem(y, nova_alt, alt)
        linha: list[Pixel] = []
        for x in range(nova_larg):
            x0, x1, tx = _origem(x, nova_larg, larg)
            topo = _mistura(imagem[y0][x0], imagem[y0][x1], tx)
            base = _mistura(imagem[y1][x0], imagem[y1][x1], tx)
            linha.append(_arredondar(_mistura(topo, base, ty)))
        saida.append(linha)
    return saida
