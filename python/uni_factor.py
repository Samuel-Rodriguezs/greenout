"""Reimplementação do factor (fatoração em primos)."""
import sys
from typing import Optional, TextIO


def fatorar(n: int) -> list[int]:
    if n < 1:
        raise ValueError("o número deve ser um inteiro positivo")
    fatores: list[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            fatores.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        fatores.append(n)
    return fatores


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    itens = argv or entrada.split()
    status = 0
    for item in itens:
        try:
            n = int(item)
            fs = fatorar(n)
        except ValueError:
            print(f"factor: '{item}' não é um inteiro positivo válido", file=sys.stderr)
            status = 1
            continue
        print(f"{n}: {' '.join(map(str, fs))}".rstrip(), file=saida)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
