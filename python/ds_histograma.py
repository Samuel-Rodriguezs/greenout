"""Histograma: contagem por faixas iguais e renderização em ASCII."""
from __future__ import annotations

from typing import Sequence


def histograma(dados: Sequence[float], n_faixas: int = 10) -> tuple[list[float], list[int]]:
    """Retorna (limites das faixas [n+1], contagens [n]). Última faixa é fechada."""
    if n_faixas <= 0:
        raise ValueError("n_faixas deve ser positivo")
    if not dados:
        raise ValueError("dados vazios")
    lo, hi = min(dados), max(dados)
    if lo == hi:
        hi = lo + 1.0
    largura = (hi - lo) / n_faixas
    limites = [lo + i * largura for i in range(n_faixas)] + [hi]
    cont = [0] * n_faixas
    for x in dados:
        cont[min(int((x - lo) / largura), n_faixas - 1)] += 1
    return limites, cont


def histograma_ascii(dados: Sequence[float], n_faixas: int = 5, largura: int = 20, simbolo: str = "#") -> str:
    limites, cont = histograma(dados, n_faixas)
    maximo = max(cont)
    rotulos = [f"[{limites[i]:.2f}, {limites[i + 1]:.2f}{']' if i == n_faixas - 1 else ')'}" for i in range(n_faixas)]
    pad = max(len(r) for r in rotulos)
    linhas = []
    for r, c in zip(rotulos, cont):
        barra = simbolo * round(c / maximo * largura) if maximo else ""
        linhas.append(f"{r.ljust(pad)} | {barra} {c}")
    return "\n".join(linhas)
