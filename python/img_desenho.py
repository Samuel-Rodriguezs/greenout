"""Desenho em matrizes: linhas (Bresenham) e círculos (ponto médio)."""

from typing import Any

Matriz = list[list[Any]]


def nova_imagem(largura: int, altura: int, valor: Any = 0) -> Matriz:
    if largura < 1 or altura < 1:
        raise ValueError("dimensões devem ser positivas")
    return [[valor] * largura for _ in range(altura)]


def pontos_linha(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Pontos (x, y) do segmento pelo algoritmo de Bresenham, em qualquer octante."""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    erro = dx + dy
    pontos = []
    while True:
        pontos.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return pontos
        e2 = 2 * erro
        if e2 >= dy:
            erro += dy
            x0 += sx
        if e2 <= dx:
            erro += dx
            y0 += sy


def pontos_circulo(cx: int, cy: int, raio: int) -> set[tuple[int, int]]:
    """Contorno do círculo pelo algoritmo do ponto médio."""
    if raio < 0:
        raise ValueError("raio não pode ser negativo")
    pontos: set[tuple[int, int]] = set()
    x, y, d = raio, 0, 1 - raio
    while x >= y:
        for px, py in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
            pontos.add((cx + px, cy + py))
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1
    return pontos


def _pintar(imagem: Matriz, pontos, valor: Any) -> None:
    for x, y in pontos:
        if 0 <= y < len(imagem) and 0 <= x < len(imagem[0]):
            imagem[y][x] = valor


def desenhar_linha(imagem: Matriz, x0: int, y0: int, x1: int, y1: int, valor: Any) -> Matriz:
    """Retorna uma cópia com a linha desenhada; pontos fora da imagem são ignorados."""
    saida = [list(l) for l in imagem]
    _pintar(saida, pontos_linha(x0, y0, x1, y1), valor)
    return saida


def desenhar_circulo(imagem: Matriz, cx: int, cy: int, raio: int, valor: Any) -> Matriz:
    saida = [list(l) for l in imagem]
    _pintar(saida, pontos_circulo(cx, cy, raio), valor)
    return saida
