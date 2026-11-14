"""Roman Calculator Kata: soma e subtração direto em numerais romanos."""
from __future__ import annotations

_TABELA = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
           (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def para_inteiro(romano: str) -> int:
    resto = romano
    total = 0
    for valor, simbolo in _TABELA:
        limite = 1 if len(simbolo) == 2 or simbolo in "VLD" else 3
        usos = 0
        while resto.startswith(simbolo):
            usos += 1
            if usos > limite:
                raise ValueError(f"numeral romano inválido: {romano}")
            total += valor
            resto = resto[len(simbolo):]
    if not romano or resto:
        raise ValueError(f"numeral romano inválido: {romano}")
    return total


def para_romano(n: int) -> str:
    if not 1 <= n <= 3999:
        raise ValueError("fora do intervalo 1..3999")
    partes = []
    for valor, simbolo in _TABELA:
        while n >= valor:
            partes.append(simbolo)
            n -= valor
    return "".join(partes)


def somar(a: str, b: str) -> str:
    return para_romano(para_inteiro(a) + para_inteiro(b))


def subtrair(a: str, b: str) -> str:
    return para_romano(para_inteiro(a) - para_inteiro(b))
