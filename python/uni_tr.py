"""Reimplementação simplificada do tr (traduzir, -d apagar)."""
import sys
from typing import Optional, TextIO


def expandir(conjunto: str) -> str:
    """Expande intervalos como 'a-e' em 'abcde'."""
    saida: list[str] = []
    i = 0
    while i < len(conjunto):
        if i + 2 < len(conjunto) and conjunto[i + 1] == "-":
            a, b = conjunto[i], conjunto[i + 2]
            if ord(a) > ord(b):
                raise ValueError(f"intervalo inválido '{a}-{b}'")
            saida.extend(chr(c) for c in range(ord(a), ord(b) + 1))
            i += 3
        else:
            saida.append(conjunto[i])
            i += 1
    return "".join(saida)


def traduzir(texto: str, origem: str, destino: str) -> str:
    o, d = expandir(origem), expandir(destino)
    if not o:
        raise ValueError("conjunto de origem vazio")
    if not d:
        raise ValueError("conjunto de destino vazio")
    d = d + d[-1] * (len(o) - len(d))  # completa com o último caractere
    tabela: dict[int, str] = {}
    for a, b in zip(o, d):
        tabela.setdefault(ord(a), b)
    return texto.translate(tabela)


def apagar(texto: str, conjunto: str) -> str:
    return texto.translate({ord(c): None for c in expandir(conjunto)})


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    try:
        if argv[:1] == ["-d"] and len(argv) == 2:
            res = apagar(entrada, argv[1])
        elif len(argv) == 2 and argv[0] != "-d":
            res = traduzir(entrada, argv[0], argv[1])
        else:
            print("uso: tr [-d] conjunto1 [conjunto2]", file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"tr: {e}", file=sys.stderr)
        return 2
    saida.write(res)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
