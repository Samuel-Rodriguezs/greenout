"""Conta dias entre duas datas (formato AAAA-MM-DD)."""
import argparse
import sys
from datetime import date
from typing import Optional, Sequence


def dias_entre(inicio: date, fim: date, util: bool = False) -> int:
    if not util:
        return (fim - inicio).days
    sinal = 1 if fim >= inicio else -1
    a, b = sorted((inicio, fim))
    total = 0
    for i in range((b - a).days):
        if date.fromordinal(a.toordinal() + i).weekday() < 5:
            total += 1
    return sinal * total


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Dias entre duas datas.")
    p.add_argument("inicio")
    p.add_argument("fim")
    p.add_argument("--uteis", action="store_true", help="conta apenas dias úteis (seg-sex)")
    a = p.parse_args(argv)
    try:
        d1, d2 = date.fromisoformat(a.inicio), date.fromisoformat(a.fim)
    except ValueError:
        print("erro: use o formato AAAA-MM-DD", file=sys.stderr)
        return 1
    n = dias_entre(d1, d2, a.uteis)
    print(f"{n} {'dias úteis' if a.uteis else 'dias'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
