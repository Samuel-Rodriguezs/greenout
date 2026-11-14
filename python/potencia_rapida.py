"""Exponenciação rápida (por quadrados), com módulo opcional."""

from typing import Optional


def potencia_rapida(base: int, expoente: int, modulo: Optional[int] = None) -> int:
    """Calcula base**expoente em O(log expoente); expoente deve ser >= 0."""
    if expoente < 0:
        raise ValueError("expoente deve ser não negativo")
    if modulo is not None and modulo <= 0:
        raise ValueError("módulo deve ser positivo")
    resultado = 1
    if modulo is not None:
        base %= modulo
        resultado %= modulo
    while expoente:
        if expoente & 1:
            resultado *= base
            if modulo is not None:
                resultado %= modulo
        base *= base
        if modulo is not None:
            base %= modulo
        expoente >>= 1
    return resultado
