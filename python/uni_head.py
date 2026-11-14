"""Reimplementação simplificada do head (-n N)."""
import sys
from typing import Optional, TextIO


def head(linhas: list[str], n: int = 10) -> list[str]:
    if n < 0:
        raise ValueError("número de linhas inválido")
    return linhas[:n]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    n = 10
    i = 0
    while i < len(argv):
        if argv[i] == "-n":
            if i + 1 >= len(argv):
                print("head: a opção -n requer um argumento", file=sys.stderr)
                return 2
            try:
                n = int(argv[i + 1])
            except ValueError:
                print(f"head: número inválido '{argv[i + 1]}'", file=sys.stderr)
                return 2
            i += 2
        else:
            print(f"head: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
    try:
        res = head(entrada.splitlines(), n)
    except ValueError as e:
        print(f"head: {e}", file=sys.stderr)
        return 2
    for l in res:
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
