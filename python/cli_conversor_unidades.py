"""Conversor de unidades (comprimento, massa e volume) em linha de comando."""
import argparse
import sys
from typing import Optional, Sequence

UNIDADES = {
    "comprimento": {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "pol": 0.0254, "pe": 0.3048, "milha": 1609.344},
    "massa": {"mg": 0.000001, "g": 0.001, "kg": 1.0, "t": 1000.0, "lb": 0.45359237, "oz": 0.028349523125},
    "volume": {"ml": 0.001, "l": 1.0, "m3": 1000.0, "gal": 3.785411784},
}


def categoria(unidade: str) -> str:
    for nome, tabela in UNIDADES.items():
        if unidade in tabela:
            return nome
    raise ValueError(f"unidade desconhecida: {unidade}")


def converter(valor: float, origem: str, destino: str) -> float:
    cat = categoria(origem)
    if categoria(destino) != cat:
        raise ValueError(f"unidades incompatíveis: {origem} e {destino}")
    return valor * UNIDADES[cat][origem] / UNIDADES[cat][destino]


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Converte valores entre unidades.")
    p.add_argument("valor", type=float)
    p.add_argument("origem")
    p.add_argument("destino")
    p.add_argument("--casas", type=int, default=4)
    a = p.parse_args(argv)
    try:
        r = converter(a.valor, a.origem, a.destino)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    print(f"{a.valor:g} {a.origem} = {round(r, a.casas):g} {a.destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
