"""Conversor de temperatura entre Celsius, Fahrenheit e Kelvin."""
import argparse
import sys
from typing import Optional, Sequence

ESCALAS = ("C", "F", "K")


def converter(valor: float, origem: str, destino: str) -> float:
    origem, destino = origem.upper(), destino.upper()
    if origem not in ESCALAS or destino not in ESCALAS:
        raise ValueError("escalas válidas: C, F, K")
    celsius = {"C": valor, "F": (valor - 32) * 5 / 9, "K": valor - 273.15}[origem]
    if celsius < -273.15 - 1e-9:
        raise ValueError("abaixo do zero absoluto")
    return {"C": celsius, "F": celsius * 9 / 5 + 32, "K": celsius + 273.15}[destino]


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Converte temperaturas.")
    p.add_argument("valor", type=float)
    p.add_argument("origem", help="C, F ou K")
    p.add_argument("destino", help="C, F ou K")
    a = p.parse_args(argv)
    try:
        r = converter(a.valor, a.origem, a.destino)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    print(f"{a.valor:g}°{a.origem.upper()} = {r:.2f}°{a.destino.upper()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
