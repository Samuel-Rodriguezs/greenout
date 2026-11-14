"""Reimplementação simplificada do sort (-r -n -u)."""
import re
import sys
from typing import Optional, TextIO

_NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")


def _chave_numerica(linha: str) -> float:
    m = _NUM.match(linha)
    return float(m.group(1)) if m else 0.0


def ordenar(linhas: list[str], reverso: bool = False, numerico: bool = False,
            unico: bool = False) -> list[str]:
    chave = _chave_numerica if numerico else None
    res = sorted(linhas, key=chave, reverse=reverso)
    if unico:
        vistos = []
        ult = object()
        for l in res:
            k = chave(l) if chave else l
            if k != ult:
                vistos.append(l)
                ult = k
        res = vistos
    return res


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    flags = set()
    arquivos = []
    for a in argv:
        if a.startswith("-") and len(a) > 1:
            if any(ch not in "rnu" for ch in a[1:]):
                print(f"sort: opção inválida -- '{a}'", file=sys.stderr)
                return 2
            flags.update(a[1:])
        else:
            arquivos.append(a)
    texto = entrada
    if arquivos:
        texto = ""
        for nome in arquivos:
            try:
                with open(nome, encoding="utf-8") as f:
                    texto += f.read()
            except OSError as e:
                print(f"sort: {nome}: {e.strerror}", file=sys.stderr)
                return 2
    for l in ordenar(texto.splitlines(), "r" in flags, "n" in flags, "u" in flags):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
