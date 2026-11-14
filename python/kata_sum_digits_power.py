"""Sum of Digits Power Kata: n = d1^1 + d2^2 + ... (ex.: 89 = 8^1 + 9^2)."""
from __future__ import annotations

from itertools import count


def soma_potencias(n: int, inicio: int = 1) -> int:
    """Soma dos dígitos elevados a potências consecutivas a partir de `inicio`."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    return sum(int(d) ** (i + inicio) for i, d in enumerate(str(n)))


def eh_potencia_digitos(n: int, inicio: int = 1) -> int:
    """Retorna k tal que soma_potencias(n, inicio) == n * k (k >= 1), ou -1 se não houver."""
    if n < 1:
        raise ValueError("n deve ser >= 1")
    soma = soma_potencias(n, inicio)
    if soma % n == 0:
        return soma // n
    return -1


def primeiros(quantidade: int) -> list[int]:
    """Primeiros números > 9 em que a soma das potências é exatamente n (k = 1)."""
    if quantidade < 0:
        raise ValueError("quantidade deve ser >= 0")
    achados: list[int] = []
    for n in count(10):
        if len(achados) == quantidade:
            break
        if soma_potencias(n) == n:
            achados.append(n)
    return achados
