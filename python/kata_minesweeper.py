"""Minesweeper Kata: contagem de minas vizinhas."""
from __future__ import annotations


def contar_vizinhos(campo: list[str]) -> list[str]:
    """Substitui cada '.' pelo número de minas ('*') adjacentes (vazio vira '0')."""
    if campo and any(len(l) != len(campo[0]) for l in campo):
        raise ValueError("linhas de tamanhos diferentes")
    if any(c not in ".*" for l in campo for c in l):
        raise ValueError("use apenas '.' e '*'")
    altura = len(campo)
    resultado = []
    for r in range(altura):
        linha = []
        for c, celula in enumerate(campo[r]):
            if celula == "*":
                linha.append("*")
                continue
            n = sum(
                campo[rr][cc] == "*"
                for rr in range(max(0, r - 1), min(altura, r + 2))
                for cc in range(max(0, c - 1), min(len(campo[r]), c + 2))
            )
            linha.append(str(n))
        resultado.append("".join(linha))
    return resultado
