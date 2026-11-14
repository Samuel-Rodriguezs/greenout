"""Cálculo da data da Páscoa (calendário gregoriano) pelo algoritmo de Meeus/Jones/Butcher."""
from __future__ import annotations

from datetime import date


def pascoa(ano: int) -> date:
    """Retorna o domingo de Páscoa do ano gregoriano informado (ano >= 1583)."""
    if ano < 1583:
        raise ValueError("o calendário gregoriano só vale a partir de 1583")
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)
