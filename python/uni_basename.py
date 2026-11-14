"""Reimplementação de basename e dirname (sintaxe POSIX)."""
import sys
from typing import Optional, TextIO


def basename(caminho: str, sufixo: str = "") -> str:
    if caminho == "":
        return ""
    limpo = caminho.rstrip("/")
    if limpo == "":
        return "/"
    nome = limpo.rsplit("/", 1)[-1]
    if sufixo and nome != sufixo and nome.endswith(sufixo):
        nome = nome[: -len(sufixo)]
    return nome


def dirname(caminho: str) -> str:
    if caminho == "":
        return "."
    limpo = caminho.rstrip("/")
    if limpo == "":
        return "/"
    if "/" not in limpo:
        return "."
    pai = limpo.rsplit("/", 1)[0].rstrip("/")
    return pai or "/"


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    """Uso: basename|dirname caminho [sufixo]."""
    saida = saida or sys.stdout
    if not argv or argv[0] not in ("basename", "dirname"):
        print("uso: uni_basename (basename|dirname) caminho [sufixo]", file=sys.stderr)
        return 2
    cmd, args = argv[0], argv[1:]
    if cmd == "dirname" and len(args) != 1:
        print("dirname: requer exatamente um caminho", file=sys.stderr)
        return 2
    if cmd == "basename" and not 1 <= len(args) <= 2:
        print("basename: uso: basename caminho [sufixo]", file=sys.stderr)
        return 2
    print(dirname(args[0]) if cmd == "dirname" else basename(*args), file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
