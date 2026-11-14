"""Reimplementação simplificada do diff usando maior subsequência comum (LCS)."""
import sys
from typing import Optional, TextIO


def lcs_tabela(a: list[str], b: list[str]) -> list[list[int]]:
    t = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            if a[i] == b[j]:
                t[i][j] = t[i + 1][j + 1] + 1
            else:
                t[i][j] = max(t[i + 1][j], t[i][j + 1])
    return t


def diff(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """Retorna operações (' ', '-', '+') com a linha correspondente."""
    t = lcs_tabela(a, b)
    i = j = 0
    ops: list[tuple[str, str]] = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            ops.append((" ", a[i]))
            i += 1
            j += 1
        elif t[i + 1][j] >= t[i][j + 1]:
            ops.append(("-", a[i]))
            i += 1
        else:
            ops.append(("+", b[j]))
            j += 1
    ops.extend(("-", x) for x in a[i:])
    ops.extend(("+", x) for x in b[j:])
    return ops


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    if len(argv) != 2:
        print("uso: diff arquivo1 arquivo2", file=sys.stderr)
        return 2
    conteudo = []
    for nome in argv:
        try:
            with open(nome, encoding="utf-8") as f:
                conteudo.append(f.read().splitlines())
        except OSError as e:
            print(f"diff: {nome}: {e.strerror}", file=sys.stderr)
            return 2
    ops = diff(*conteudo)
    diferente = False
    for op, linha in ops:
        if op != " ":
            diferente = True
            print(f"{op} {linha}", file=saida)
    return 1 if diferente else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
