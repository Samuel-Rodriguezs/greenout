"""Diamond Kata: losango de letras."""
from __future__ import annotations


def losango(letra: str) -> str:
    if len(letra) != 1 or not letra.isalpha() or not letra.isascii():
        raise ValueError("informe uma única letra A-Z")
    letra = letra.upper()
    n = ord(letra) - ord("A")
    linhas = []
    for i in range(n + 1):
        c = chr(ord("A") + i)
        meio = c if i == 0 else c + " " * (2 * i - 1) + c
        linhas.append(" " * (n - i) + meio + " " * (n - i))
    return "\n".join(linhas + linhas[-2::-1])
