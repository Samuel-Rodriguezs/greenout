"""Reimplementação simplificada do uniq (-c -d)."""
import sys
from typing import Optional, TextIO


def agrupar(linhas: list[str]) -> list[tuple[str, int]]:
    """Agrupa linhas adjacentes iguais, como o uniq."""
    grupos: list[tuple[str, int]] = []
    for l in linhas:
        if grupos and grupos[-1][0] == l:
            grupos[-1] = (l, grupos[-1][1] + 1)
        else:
            grupos.append((l, 1))
    return grupos


def uniq(linhas: list[str], contar: bool = False, duplicadas: bool = False) -> list[str]:
    saida = []
    for l, n in agrupar(linhas):
        if duplicadas and n < 2:
            continue
        saida.append(f"{n:7d} {l}" if contar else l)
    return saida


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    flags = set()
    for a in argv:
        if a.startswith("-") and len(a) > 1 and all(ch in "cd" for ch in a[1:]):
            flags.update(a[1:])
        else:
            print(f"uniq: argumento inválido '{a}'", file=sys.stderr)
            return 2
    for l in uniq(entrada.splitlines(), "c" in flags, "d" in flags):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
