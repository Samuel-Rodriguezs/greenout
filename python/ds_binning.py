"""Agrupamento por faixas (binning): limites manuais, largura igual e quantis."""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Sequence


def _validar_limites(limites: Sequence[float]) -> list[float]:
    lim = list(limites)
    if len(lim) < 2:
        raise ValueError("são necessários ao menos 2 limites")
    if any(b <= a for a, b in zip(lim, lim[1:])):
        raise ValueError("limites devem ser estritamente crescentes")
    return lim


def rotulos_faixas(limites: Sequence[float], direita: bool = True) -> list[str]:
    lim = _validar_limites(limites)
    abre, fecha = ("(", "]") if direita else ("[", ")")
    return [f"{abre}{a:g}, {b:g}{fecha}" for a, b in zip(lim, lim[1:])]


def indice_faixa(
    x: float, limites: Sequence[float], direita: bool = True, incluir_extremo: bool = True
) -> int | None:
    """Índice da faixa de x, ou None se fora. Faixas (a,b] se direita, senão [a,b)."""
    lim = _validar_limites(limites)
    n = len(lim) - 1
    if direita:
        i = bisect_left(lim, x) - 1
        if incluir_extremo and x == lim[0]:
            i = 0
    else:
        i = bisect_right(lim, x) - 1
        if incluir_extremo and x == lim[-1]:
            i = n - 1
    return i if 0 <= i < n else None


def cortar(
    valores: Sequence[float],
    limites: Sequence[float],
    direita: bool = True,
    incluir_extremo: bool = False,
    rotulos: Sequence[str] | None = None,
) -> list[str | None]:
    lim = _validar_limites(limites)
    nomes = list(rotulos) if rotulos is not None else rotulos_faixas(lim, direita)
    if len(nomes) != len(lim) - 1:
        raise ValueError("número de rótulos deve ser len(limites) - 1")
    saida: list[str | None] = []
    for v in valores:
        i = indice_faixa(v, lim, direita, incluir_extremo)
        saida.append(None if i is None else nomes[i])
    return saida


def limites_largura_igual(valores: Sequence[float], n_faixas: int) -> list[float]:
    if n_faixas <= 0 or not valores:
        raise ValueError("n_faixas positivo e valores não vazios")
    lo, hi = min(valores), max(valores)
    if lo == hi:
        raise ValueError("todos os valores são iguais")
    passo = (hi - lo) / n_faixas
    return [lo + i * passo for i in range(n_faixas)] + [hi]


def limites_quantis(valores: Sequence[float], n_faixas: int) -> list[float]:
    if n_faixas <= 0 or not valores:
        raise ValueError("n_faixas positivo e valores não vazios")
    s = sorted(valores)
    saida = []
    for k in range(n_faixas + 1):
        pos = k / n_faixas * (len(s) - 1)
        i = int(pos)
        saida.append(s[-1] if i + 1 >= len(s) else s[i] + (pos - i) * (s[i + 1] - s[i]))
    return saida


def contar_por_faixa(valores: Sequence[float], limites: Sequence[float], direita: bool = True) -> dict[str, int]:
    nomes = rotulos_faixas(limites, direita)
    cont = {n: 0 for n in nomes}
    for r in cortar(valores, limites, direita, incluir_extremo=True):
        if r is not None:
            cont[r] += 1
    return cont
