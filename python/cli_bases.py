"""Conversor de bases numéricas (2 a 36) em linha de comando."""
import argparse
import sys
from typing import Optional, Sequence

DIGITOS = "0123456789abcdefghijklmnopqrstuvwxyz"


def para_base(n: int, base: int) -> str:
    if not 2 <= base <= 36:
        raise ValueError("base deve estar entre 2 e 36")
    if n == 0:
        return "0"
    sinal = "-" if n < 0 else ""
    n = abs(n)
    out = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITOS[r])
    return sinal + "".join(reversed(out))


def de_base(texto: str, base: int) -> int:
    if not 2 <= base <= 36:
        raise ValueError("base deve estar entre 2 e 36")
    return int(texto, base)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Converte números entre bases.")
    p.add_argument("numero")
    p.add_argument("--de", type=int, default=10, dest="origem")
    p.add_argument("--para", type=int, default=2, dest="destino")
    a = p.parse_args(argv)
    try:
        print(para_base(de_base(a.numero, a.origem), a.destino))
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
