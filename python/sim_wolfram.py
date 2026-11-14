"""Autômato celular unidimensional (regras de Wolfram)."""
from __future__ import annotations


def tabela_regra(numero: int) -> dict[tuple[int, int, int], int]:
    if not 0 <= numero <= 255:
        raise ValueError("regra deve estar entre 0 e 255")
    return {
        (a, b, c): (numero >> (a * 4 + b * 2 + c)) & 1
        for a in (0, 1) for b in (0, 1) for c in (0, 1)
    }


def proxima_geracao(celulas: list[int], regra: int, circular: bool = True) -> list[int]:
    t = tabela_regra(regra)
    n = len(celulas)
    saida = []
    for i in range(n):
        if circular:
            e, d = celulas[(i - 1) % n], celulas[(i + 1) % n]
        else:
            e = celulas[i - 1] if i > 0 else 0
            d = celulas[i + 1] if i < n - 1 else 0
        saida.append(t[(e, celulas[i], d)])
    return saida


def simular(regra: int, largura: int, geracoes: int, inicial: list[int] | None = None,
            circular: bool = True) -> list[list[int]]:
    if inicial is None:
        inicial = [0] * largura
        inicial[largura // 2] = 1
    if len(inicial) != largura:
        raise ValueError("estado inicial com largura incorreta")
    hist = [list(inicial)]
    for _ in range(geracoes):
        hist.append(proxima_geracao(hist[-1], regra, circular))
    return hist


def renderizar(hist: list[list[int]]) -> str:
    return "\n".join("".join("#" if c else "." for c in linha) for linha in hist)
