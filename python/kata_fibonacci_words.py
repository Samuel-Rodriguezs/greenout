"""Fibonacci Words Kata: S(0)="0", S(1)="01", S(n)=S(n-1)+S(n-2)."""
from __future__ import annotations

from collections.abc import Iterator


def palavra(n: int) -> str:
    if n < 0:
        raise ValueError("n deve ser >= 0")
    anterior, atual = "0", "01"
    if n == 0:
        return anterior
    for _ in range(n - 1):
        anterior, atual = atual, atual + anterior
    return atual


def palavras(limite: int) -> Iterator[str]:
    """Gera S(0)..S(limite-1)."""
    for i in range(limite):
        yield palavra(i)


def comprimento(n: int) -> int:
    """Calcula |S(n)| sem construir a palavra (números de Fibonacci)."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    a, b = 1, 2
    for _ in range(n):
        a, b = b, a + b
    return a


def caractere(n: int) -> str:
    """n-ésimo (base 0) caractere da palavra infinita, sem montar a palavra inteira."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    k = 0
    while comprimento(k) <= n:
        k += 1
    # S(k) = S(k-1) + S(k-2); desce até S(0) = "0" ou S(1) = "01".
    while k > 1:
        tam = comprimento(k - 1)
        if n < tam:
            k -= 1
        else:
            n -= tam
            k -= 2
    return "0" if k == 0 else "01"[n]


def palavra_infinita_prefixo(tamanho: int) -> str:
    """Prefixo da palavra de Fibonacci infinita com o tamanho pedido."""
    if tamanho < 0:
        raise ValueError("tamanho deve ser >= 0")
    s = "0"
    anterior, atual = "0", "01"
    while len(s) < tamanho:
        s = atual
        anterior, atual = atual, atual + anterior
    return s[:tamanho]
