"""Reimplementação simplificada do tail (-n N)."""
import sys
from typing import Optional, TextIO


def tail(linhas: list[str], n: int = 10) -> list[str]:
    if n < 0:
        raise ValueError("número de linhas inválido")
    return linhas[len(linhas) - n:] if n else []


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    n = 10
    i = 0
    while i < len(argv):
        if argv[i] == "-n" and i + 1 < len(argv):
            try:
                n = int(argv[i + 1])
            except ValueError:
                print(f"tail: número inválido '{argv[i + 1]}'", file=sys.stderr)
                return 2
            i += 2
        else:
            print(f"tail: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
    try:
        res = tail(entrada.splitlines(), n)
    except ValueError as e:
        print(f"tail: {e}", file=sys.stderr)
        return 2
    for l in res:
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
