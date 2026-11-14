"""Calculadora de juros compostos com aportes mensais opcionais."""
import argparse
import sys
from typing import Optional, Sequence


def montante(capital: float, taxa_mensal: float, meses: int, aporte: float = 0.0) -> float:
    """Montante final; aportes feitos ao fim de cada mês."""
    if capital < 0 or aporte < 0 or taxa_mensal < 0 or meses < 0:
        raise ValueError("valores não podem ser negativos")
    saldo = capital
    for _ in range(meses):
        saldo = saldo * (1 + taxa_mensal) + aporte
    return saldo


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Juros compostos.")
    p.add_argument("--capital", type=float, required=True)
    p.add_argument("--taxa", type=float, required=True, help="taxa mensal em %%")
    p.add_argument("--meses", type=int, required=True)
    p.add_argument("--aporte", type=float, default=0.0, help="aporte mensal")
    p.add_argument("--anual", action="store_true", help="interpreta a taxa como anual e converte para mensal")
    a = p.parse_args(argv)
    taxa = a.taxa / 100
    if a.anual:
        taxa = (1 + taxa) ** (1 / 12) - 1
    try:
        final = montante(a.capital, taxa, a.meses, a.aporte)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    investido = a.capital + a.aporte * a.meses
    print(f"Montante: {final:.2f}")
    print(f"Investido: {investido:.2f}")
    print(f"Juros: {final - investido:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
