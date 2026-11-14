"""Calculadora de gorjeta com divisão da conta."""
import argparse
import sys
from typing import Optional, Sequence, Tuple


def calcular(conta: float, percentual: float, pessoas: int = 1) -> Tuple[float, float, float]:
    """Retorna (gorjeta, total, valor por pessoa)."""
    if conta < 0 or percentual < 0:
        raise ValueError("conta e percentual não podem ser negativos")
    if pessoas < 1:
        raise ValueError("pessoas deve ser >= 1")
    gorjeta = conta * percentual / 100
    total = conta + gorjeta
    return gorjeta, total, total / pessoas


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Calcula gorjeta e divisão da conta.")
    p.add_argument("conta", type=float)
    p.add_argument("-p", "--percentual", type=float, default=10.0)
    p.add_argument("-n", "--pessoas", type=int, default=1)
    a = p.parse_args(argv)
    try:
        gorjeta, total, por_pessoa = calcular(a.conta, a.percentual, a.pessoas)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    print(f"Gorjeta: {gorjeta:.2f}")
    print(f"Total: {total:.2f}")
    if a.pessoas > 1:
        print(f"Por pessoa: {por_pessoa:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
