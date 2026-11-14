"""Área da união de retângulos alinhados aos eixos (sweep line, O(n^2))."""
from __future__ import annotations

Retangulo = tuple[float, float, float, float]  # (x1, y1, x2, y2) com x1<x2, y1<y2


def _comprimento_uniao(intervalos: list[tuple[float, float]]) -> float:
    total = 0.0
    fim = None
    for a, b in sorted(intervalos):
        if fim is None or a > fim:
            total += b - a
            fim = b
        elif b > fim:
            total += b - fim
            fim = b
    return total


def area_uniao(retangulos: list[Retangulo]) -> float:
    """Área coberta por ao menos um retângulo (sobreposições contam uma vez)."""
    for x1, y1, x2, y2 in retangulos:
        if x1 > x2 or y1 > y2:
            raise ValueError(f"retângulo invertido: {(x1, y1, x2, y2)}")
    validos = [r for r in retangulos if r[0] < r[2] and r[1] < r[3]]
    xs = sorted({x for r in validos for x in (r[0], r[2])})
    total = 0.0
    for xa, xb in zip(xs, xs[1:]):
        faixa = [(r[1], r[3]) for r in validos if r[0] <= xa and xb <= r[2]]
        total += (xb - xa) * _comprimento_uniao(faixa)
    return total


def area_soma_simples(retangulos: list[Retangulo]) -> float:
    """Soma das áreas sem descontar sobreposição (para comparação)."""
    return sum((x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in retangulos)


def area_sobreposta(retangulos: list[Retangulo]) -> float:
    """Área contada mais de uma vez pela soma simples."""
    return area_soma_simples(retangulos) - area_uniao(retangulos)
