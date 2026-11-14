"""Kaprekar Kata: rotina de Kaprekar (6174) e números de Kaprekar."""
from __future__ import annotations

CONSTANTE = 6174


def passo(n: int) -> int:
    """Um passo: maior permutação dos 4 dígitos menos a menor (com zeros à esquerda)."""
    if not 0 <= n <= 9999:
        raise ValueError("n deve ter até 4 dígitos")
    digitos = f"{n:04d}"
    if len(set(digitos)) == 1:
        raise ValueError("todos os dígitos iguais não convergem")
    crescente = "".join(sorted(digitos))
    return int(crescente[::-1]) - int(crescente)


def passos_ate_6174(n: int) -> int:
    """Quantidade de passos até chegar a 6174 (no máximo 7)."""
    passos = 0
    while n != CONSTANTE:
        n = passo(n)
        passos += 1
    return passos


def eh_kaprekar(n: int) -> bool:
    """n é de Kaprekar se n² dividido em duas partes soma n (parte direita > 0)."""
    if n < 1:
        raise ValueError("n deve ser positivo")
    if n == 1:
        return True
    quadrado = str(n * n)
    for corte in range(1, len(quadrado)):
        esq, dir_ = int(quadrado[:corte]), int(quadrado[corte:])
        if dir_ > 0 and esq + dir_ == n:
            return True
    return False
