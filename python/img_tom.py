"""Ajustes tonais em imagens de cinza: brilho, contraste, gama, inversão e limiar."""

Imagem = list[list[int]]


def _limitar(v: float) -> int:
    return max(0, min(255, round(v)))


def ajustar_brilho(imagem: Imagem, delta: int) -> Imagem:
    return [[_limitar(v + delta) for v in linha] for linha in imagem]


def ajustar_contraste(imagem: Imagem, fator: float) -> Imagem:
    """Expande (fator > 1) ou comprime (< 1) os valores em torno de 128."""
    return [[_limitar((v - 128) * fator + 128) for v in linha] for linha in imagem]


def corrigir_gama(imagem: Imagem, gama: float) -> Imagem:
    """gama > 1 clareia os tons médios; gama < 1 escurece."""
    if gama <= 0:
        raise ValueError("gama deve ser positivo")
    return [[_limitar(255 * (v / 255) ** (1 / gama)) for v in linha] for linha in imagem]


def inverter(imagem: Imagem) -> Imagem:
    return [[255 - v for v in linha] for linha in imagem]


def limiarizar(imagem: Imagem, limiar: int, alto: int = 255, baixo: int = 0) -> Imagem:
    """Pixels >= limiar viram `alto`; os demais viram `baixo`."""
    return [[alto if v >= limiar else baixo for v in linha] for linha in imagem]
