"""Reimplementação simplificada do fold (-w largura, -s quebra em espaços)."""
import sys
from typing import Optional, TextIO


def dobrar_linha(linha: str, largura: int = 80, em_espacos: bool = False) -> list[str]:
    if largura < 1:
        raise ValueError("largura deve ser positiva")
    partes = []
    while len(linha) > largura:
        corte = largura
        if em_espacos:
            pos = linha.rfind(" ", 0, largura)
            if pos != -1:
                corte = pos + 1
        partes.append(linha[:corte])
        linha = linha[corte:]
    partes.append(linha)
    return partes


def dobrar(linhas: list[str], largura: int = 80, em_espacos: bool = False) -> list[str]:
    saida: list[str] = []
    for l in linhas:
        saida.extend(dobrar_linha(l, largura, em_espacos))
    return saida


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    largura, espacos = 80, False
    i = 0
    while i < len(argv):
        if argv[i] == "-s":
            espacos = True
            i += 1
        elif argv[i] == "-w" and i + 1 < len(argv):
            try:
                largura = int(argv[i + 1])
            except ValueError:
                print(f"fold: largura inválida '{argv[i + 1]}'", file=sys.stderr)
                return 2
            i += 2
        else:
            print(f"fold: argumento inválido '{argv[i]}'", file=sys.stderr)
            return 2
    try:
        res = dobrar(entrada.splitlines(), largura, espacos)
    except ValueError as e:
        print(f"fold: {e}", file=sys.stderr)
        return 2
    for l in res:
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
