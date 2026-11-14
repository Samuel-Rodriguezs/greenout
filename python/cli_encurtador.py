"""Encurtador de URLs local, com mapeamento salvo em JSON."""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

ALFABETO = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def codigo(n: int) -> str:
    if n == 0:
        return ALFABETO[0]
    out = []
    while n:
        n, r = divmod(n, len(ALFABETO))
        out.append(ALFABETO[r])
    return "".join(reversed(out))


def carregar(caminho: Path) -> Dict[str, str]:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {}


def encurtar(mapa: Dict[str, str], url: str) -> str:
    for c, u in mapa.items():
        if u == url:
            return c
    c = codigo(len(mapa) + 1)
    mapa[c] = url
    return c


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Encurtador de URLs local.")
    p.add_argument("--arquivo", default="links.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("encurtar").add_argument("url")
    sub.add_parser("resolver").add_argument("codigo")
    sub.add_parser("listar")
    a = p.parse_args(argv)

    caminho = Path(a.arquivo)
    mapa = carregar(caminho)
    if a.cmd == "encurtar":
        if not a.url.startswith(("http://", "https://")):
            print("erro: a URL deve começar com http:// ou https://", file=sys.stderr)
            return 1
        c = encurtar(mapa, a.url)
        caminho.write_text(json.dumps(mapa), encoding="utf-8")
        print(c)
    elif a.cmd == "resolver":
        if a.codigo not in mapa:
            print("erro: código não encontrado", file=sys.stderr)
            return 1
        print(mapa[a.codigo])
    else:
        for c, u in mapa.items():
            print(f"{c} -> {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
