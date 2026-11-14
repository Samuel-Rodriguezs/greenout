"""Gerador de tabuada em linha de comando."""
import argparse
import sys
from typing import List, Optional, Sequence


def tabuada(n: int, inicio: int = 1, fim: int = 10) -> List[str]:
    if inicio > fim:
        raise ValueError("início deve ser <= fim")
    return [f"{n} x {i} = {n * i}" for i in range(inicio, fim + 1)]


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gera a tabuada de um ou mais números.")
    p.add_argument("numeros", nargs="+", type=int)
    p.add_argument("--inicio", type=int, default=1)
    p.add_argument("--fim", type=int, default=10)
    a = p.parse_args(argv)
    try:
        blocos = ["\n".join(tabuada(n, a.inicio, a.fim)) for n in a.numeros]
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    print("\n\n".join(blocos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
