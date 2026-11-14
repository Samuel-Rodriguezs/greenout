"""Reimplementação simplificada do nl / cat -n (numerar linhas)."""
import sys
from typing import Optional, TextIO


def numerar(linhas: list[str], inicio: int = 1, ignorar_vazias: bool = False) -> list[str]:
    """Numera linhas. Com ignorar_vazias, linhas vazias não são numeradas (nl)."""
    saida = []
    n = inicio
    for l in linhas:
        if ignorar_vazias and l == "":
            saida.append("")
            continue
        saida.append(f"{n:6d}\t{l}")
        n += 1
    return saida


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    inicio, ignorar = 1, False
    i = 0
    while i < len(argv):
        if argv[i] == "-b":
            ignorar = True
            i += 1
        elif argv[i] == "-v" and i + 1 < len(argv):
            try:
                inicio = int(argv[i + 1])
            except ValueError:
                print(f"nl: número inválido '{argv[i + 1]}'", file=sys.stderr)
                return 2
            i += 2
        else:
            print(f"nl: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
    for l in numerar(entrada.splitlines(), inicio, ignorar):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
