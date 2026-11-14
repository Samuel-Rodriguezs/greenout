"""Resumo de arquivos de log: contagem por nível e erros mais frequentes."""
import argparse
import re
import sys
from collections import Counter
from typing import Dict, Iterable, Optional, Sequence, Tuple

NIVEIS = ("DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL")
PADRAO = re.compile(r"\b(" + "|".join(NIVEIS) + r")\b[:\s-]*(.*)")


def resumir(linhas: Iterable[str]) -> Tuple[Dict[str, int], Counter]:
    por_nivel: Counter = Counter()
    erros: Counter = Counter()
    for linha in linhas:
        m = PADRAO.search(linha)
        if not m:
            continue
        nivel = "WARNING" if m.group(1) == "WARN" else m.group(1)
        por_nivel[nivel] += 1
        if nivel in ("ERROR", "CRITICAL") and m.group(2).strip():
            erros[m.group(2).strip()] += 1
    return dict(por_nivel), erros


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Resume um arquivo de log.")
    p.add_argument("arquivo")
    p.add_argument("--top", type=int, default=3, help="quantos erros mais frequentes mostrar")
    a = p.parse_args(argv)
    try:
        with open(a.arquivo, encoding="utf-8") as f:
            por_nivel, erros = resumir(f)
    except OSError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    for nivel in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        if nivel in por_nivel:
            print(f"{nivel}: {por_nivel[nivel]}")
    if erros:
        print("erros mais frequentes:")
        for msg, n in sorted(erros.items(), key=lambda kv: (-kv[1], kv[0]))[: a.top]:
            print(f"  {n}x {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
