"""Reimplementação do rev (inverte os caracteres de cada linha)."""
import sys
from typing import Optional, TextIO


def inverter_linhas(linhas: list[str]) -> list[str]:
    return [l[::-1] for l in linhas]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    if argv:
        print(f"rev: argumento inválido '{argv[0]}'", file=sys.stderr)
        return 2
    for l in inverter_linhas(entrada.splitlines()):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
