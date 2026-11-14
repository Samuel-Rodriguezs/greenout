"""Conversões de cor: RGB para cinza e RGB <-> HSV."""

RGB = tuple[int, int, int]
HSV = tuple[float, float, float]


def pixel_para_cinza(pixel: RGB) -> int:
    """Luminância ITU-R BT.601 arredondada."""
    r, g, b = pixel
    return round(0.299 * r + 0.587 * g + 0.114 * b)


def rgb_para_cinza(imagem: list[list[RGB]]) -> list[list[int]]:
    return [[pixel_para_cinza(p) for p in linha] for linha in imagem]


def cinza_para_rgb(imagem: list[list[int]]) -> list[list[RGB]]:
    return [[(v, v, v) for v in linha] for linha in imagem]


def rgb_para_hsv(pixel: RGB) -> HSV:
    """Retorna (matiz 0-360, saturação 0-1, valor 0-1)."""
    r, g, b = (c / 255 for c in pixel)
    maior, menor = max(r, g, b), min(r, g, b)
    delta = maior - menor
    if delta == 0:
        h = 0.0
    elif maior == r:
        h = 60 * (((g - b) / delta) % 6)
    elif maior == g:
        h = 60 * ((b - r) / delta + 2)
    else:
        h = 60 * ((r - g) / delta + 4)
    s = 0.0 if maior == 0 else delta / maior
    return h, s, maior


def hsv_para_rgb(pixel: HSV) -> RGB:
    h, s, v = pixel
    h %= 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    sector = int(h // 60)
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][sector]
    return round((r + m) * 255), round((g + m) * 255), round((b + m) * 255)
