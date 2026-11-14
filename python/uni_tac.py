"""Reimplementação do tac (imprime as linhas em ordem inversa)."""
import sys
from typing import Optional, TextIO


def tac(linhas: list[str]) -> list[str]:
    return linhas[::-1]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    texto = entrada
    if argv:
        texto = ""
        for nome in argv:
            try:
                with open(nome, encoding="utf-8") as f:
                    texto += f.read()
            except OSError as e:
                print(f"tac: {nome}: {e.strerror}", file=sys.stderr)
                return 1
    for l in tac(texto.splitlines()):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
