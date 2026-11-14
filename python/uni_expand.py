"""Reimplementação simplificada do expand (tabs -> espaços) e unexpand."""
import sys
from typing import Optional, TextIO


def expandir_linha(linha: str, tab: int = 8) -> str:
    if tab < 1:
        raise ValueError("tamanho de tabulação deve ser positivo")
    saida = []
    col = 0
    for ch in linha:
        if ch == "\t":
            n = tab - col % tab
            saida.append(" " * n)
            col += n
        else:
            saida.append(ch)
            col += 1
    return "".join(saida)


def desexpandir_linha(linha: str, tab: int = 8) -> str:
    """Converte espaços iniciais em tabs sempre que alcançam um tab stop."""
    if tab < 1:
        raise ValueError("tamanho de tabulação deve ser positivo")
    n = len(linha) - len(linha.lstrip(" "))
    return "\t" * (n // tab) + " " * (n % tab) + linha[n:]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    tab, inverso = 8, False
    i = 0
    while i < len(argv):
        if argv[i] == "-u":
            inverso = True
            i += 1
        elif argv[i] == "-t" and i + 1 < len(argv):
            try:
                tab = int(argv[i + 1])
            except ValueError:
                print(f"expand: tamanho inválido '{argv[i + 1]}'", file=sys.stderr)
                return 2
            i += 2
        else:
            print(f"expand: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
    f = desexpandir_linha if inverso else expandir_linha
    try:
        for l in entrada.splitlines():
            print(f(l, tab), file=saida)
    except ValueError as e:
        print(f"expand: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
