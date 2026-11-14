"""Reimplementação simplificada do paste (-d delimitador, -s serial)."""
import sys
from typing import Optional, TextIO


def colar(colunas: list[list[str]], delim: str = "\t") -> list[str]:
    """Cola linha a linha várias listas; as mais curtas são completadas com ''."""
    if not colunas:
        return []
    total = max(len(c) for c in colunas)
    return [delim.join(c[i] if i < len(c) else "" for c in colunas)
            for i in range(total)]


def colar_serial(colunas: list[list[str]], delim: str = "\t") -> list[str]:
    return [delim.join(c) for c in colunas]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    delim, serial, arquivos = "\t", False, []
    i = 0
    while i < len(argv):
        if argv[i] == "-s":
            serial = True
            i += 1
        elif argv[i] == "-d" and i + 1 < len(argv):
            delim = argv[i + 1]
            i += 2
        elif argv[i].startswith("-") and argv[i] != "-":
            print(f"paste: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
        else:
            arquivos.append(argv[i])
            i += 1
    colunas = []
    if not arquivos:
        colunas.append(entrada.splitlines())
    for nome in arquivos:
        if nome == "-":
            colunas.append(entrada.splitlines())
            continue
        try:
            with open(nome, encoding="utf-8") as f:
                colunas.append(f.read().splitlines())
        except OSError as e:
            print(f"paste: {nome}: {e.strerror}", file=sys.stderr)
            return 1
    for l in (colar_serial if serial else colar)(colunas, delim):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
