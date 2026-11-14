"""Leap Year Kata: ano bissexto no calendário gregoriano."""
from __future__ import annotations


def bissexto(ano: int) -> bool:
    """Divisível por 4, exceto séculos que não sejam divisíveis por 400."""
    if ano < 1:
        raise ValueError("ano deve ser positivo")
    return ano % 400 == 0 or (ano % 4 == 0 and ano % 100 != 0)


def dias_no_ano(ano: int) -> int:
    return 366 if bissexto(ano) else 365
