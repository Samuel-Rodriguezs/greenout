"""Problema das moedas falsas: busca da moeda diferente com balança de dois pratos."""
from __future__ import annotations

from math import ceil, log
from typing import Callable, Optional

# Balança: recebe (índices à esquerda, índices à direita) e devolve -1, 0 ou 1
# (esquerda mais leve, equilíbrio, esquerda mais pesada).
Balanca = Callable[[list[int], list[int]], int]


def balanca_para(pesos: list[int]) -> tuple[Balanca, list[int]]:
    """Cria uma balança sobre `pesos` e uma lista que registra cada pesagem."""
    usos: list[int] = []

    def pesar(esq: list[int], dir_: list[int]) -> int:
        if len(esq) != len(dir_):
            raise ValueError("pratos com quantidades diferentes")
        usos.append(1)
        a, b = sum(pesos[i] for i in esq), sum(pesos[i] for i in dir_)
        return (a > b) - (a < b)

    return pesar, usos


def pesagens_minimas_leve_conhecida(n: int) -> int:
    """Moeda mais leve (sabe-se que existe): ceil(log3 n) pesagens."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    return 0 if n == 1 else ceil(log(n, 3) - 1e-12)


def achar_mais_leve(n: int, pesar: Balanca) -> int:
    """Divide em três grupos iguais (ou quase) e descarta dois por pesagem."""
    candidatas = list(range(n))
    while len(candidatas) > 1:
        t = ceil(len(candidatas) / 3)
        g1, g2, g3 = candidatas[:t], candidatas[t:2 * t], candidatas[2 * t:]
        r = pesar(g1, g2)
        candidatas = g1 if r < 0 else g2 if r > 0 else g3
    return candidatas[0]


def achar_diferente_12(pesar: Balanca) -> tuple[int, str]:
    """12 moedas, uma diferente (mais leve ou mais pesada, desconhecido) em 3 pesagens.

    Retorna (índice, 'leve'|'pesada').
    """
    def veredito(idx: int, tipo: str) -> tuple[int, str]:
        return idx, tipo

    r1 = pesar([0, 1, 2, 3], [4, 5, 6, 7])
    if r1 == 0:
        # a diferente está entre 8..11; 0..7 são verdadeiras
        r2 = pesar([8, 9], [10, 0])
        if r2 == 0:
            r3 = pesar([11], [0])
            return veredito(11, "leve" if r3 < 0 else "pesada")
        # r2 < 0: 8 ou 9 leve, ou 10 pesada; r2 > 0: 8 ou 9 pesada, ou 10 leve
        r3 = pesar([8], [9])
        if r3 == 0:
            return veredito(10, "pesada" if r2 < 0 else "leve")
        if r2 < 0:
            return veredito(8 if r3 < 0 else 9, "leve")
        return veredito(8 if r3 > 0 else 9, "pesada")
    # r1 != 0: considere "esq mais leve" (r1 < 0) -> ou uma de 0..3 é leve, ou uma de 4..7 é pesada
    # (se r1 > 0, simétrico: trocamos os papéis)
    a, b = ([0, 1, 2, 3], [4, 5, 6, 7]) if r1 < 0 else ([4, 5, 6, 7], [0, 1, 2, 3])
    # a: suspeitas de leve; b: suspeitas de pesada
    r2 = pesar([a[0], a[1], b[0]], [a[2], b[1], 8])
    if r2 == 0:
        # sobraram a[3] (leve), b[2] ou b[3] (pesadas)
        r3 = pesar([b[2]], [b[3]])
        if r3 == 0:
            return veredito(a[3], "leve")
        return veredito(b[2] if r3 > 0 else b[3], "pesada")
    if r2 < 0:
        # esquerda mais leve: a[0] ou a[1] leve, ou b[1] pesada
        r3 = pesar([a[0]], [a[1]])
        if r3 == 0:
            return veredito(b[1], "pesada")
        return veredito(a[0] if r3 < 0 else a[1], "leve")
    # esquerda mais pesada: b[0] pesada, ou a[2] leve
    r3 = pesar([a[2]], [8])
    if r3 == 0:
        return veredito(b[0], "pesada")
    return veredito(a[2], "leve")


def pesagens_necessarias_desconhecida(n: int) -> Optional[int]:
    """Limite inferior de informação: (3^k - 3)/2 >= n para achar a moeda e dizer se é leve/pesada."""
    if n < 3:
        return None  # sem moeda de referência não há como decidir
    k = 2
    while (3 ** k - 3) // 2 < n:
        k += 1
    return k
