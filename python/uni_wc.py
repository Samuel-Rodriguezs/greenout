"""Reimplementação simplificada do utilitário wc."""
import sys
from typing import Optional, TextIO


def contar(texto: str) -> tuple[int, int, int]:
    """Retorna (linhas, palavras, bytes) como o wc."""
    return texto.count("\n"), len(texto.split()), len(texto.encode("utf-8"))


def formatar(valores: tuple[int, int, int], opcoes: str) -> str:
    l, p, c = valores
    mapa = {"l": l, "w": p, "c": c}
    escolhidas = [o for o in "lwc" if o in opcoes] or list("lwc")
    return " ".join(str(mapa[o]) for o in escolhidas)


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    opcoes = ""
    arquivos = []
    for a in argv:
        if a.startswith("-") and len(a) > 1:
            if any(ch not in "lwc" for ch in a[1:]):
                print(f"wc: opção inválida -- '{a}'", file=sys.stderr)
                return 2
            opcoes += a[1:]
        else:
            arquivos.append(a)
    if not arquivos:
        print(formatar(contar(entrada), opcoes), file=saida)
        return 0
    status = 0
    for nome in arquivos:
        try:
            with open(nome, encoding="utf-8") as f:
                texto = f.read()
        except OSError as e:
            print(f"wc: {nome}: {e.strerror}", file=sys.stderr)
            status = 1
            continue
        print(f"{formatar(contar(texto), opcoes)} {nome}", file=saida)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
