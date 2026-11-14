"""Realce de nitidez (sharpen): kernel clássico e máscara de nitidez (unsharp mask)."""

from img_blur import blur_gaussiano
from img_convolucao import convolver, limitar

Imagem = list[list[int]]

KERNEL_NITIDEZ = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]


def afiar(imagem: Imagem, borda: str = "replicar") -> Imagem:
    """Aplica o kernel de nitidez 3x3 (soma 1, preserva regiões planas)."""
    return limitar(convolver(imagem, KERNEL_NITIDEZ, borda))


def mascara_nitidez(imagem: Imagem, quantidade: float = 1.0, raio: int = 1,
                    sigma: float = 1.0) -> Imagem:
    """resultado = original + quantidade * (original - desfocada)."""
    desfocada = blur_gaussiano(imagem, raio, sigma)
    return limitar([[o + quantidade * (o - d) for o, d in zip(lo, ld)]
                    for lo, ld in zip(imagem, desfocada)])
