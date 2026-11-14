"""Calculadora de IMC em linha de comando."""
import argparse
import sys
from typing import Optional, Sequence


def calcular_imc(peso: float, altura: float) -> float:
    if peso <= 0 or altura <= 0:
        raise ValueError("peso e altura devem ser positivos")
    return peso / (altura ** 2)


def classificar(imc: float) -> str:
    if imc < 18.5:
        return "abaixo do peso"
    if imc < 25:
        return "peso normal"
    if imc < 30:
        return "sobrepeso"
    if imc < 35:
        return "obesidade grau I"
    if imc < 40:
        return "obesidade grau II"
    return "obesidade grau III"


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Calcula o IMC.")
    p.add_argument("--peso", type=float, required=True, help="peso em kg")
    p.add_argument("--altura", type=float, required=True, help="altura em metros")
    a = p.parse_args(argv)
    try:
        imc = calcular_imc(a.peso, a.altura)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    print(f"IMC: {imc:.2f} ({classificar(imc)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
