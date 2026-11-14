"""Cronograma de estudos: distribui matérias nos dias de estudo proporcionalmente aos pesos."""
import argparse
import sys
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Tuple


def distribuir(materias: Dict[str, int], horas_totais: int) -> Dict[str, int]:
    """Distribui horas inteiras por peso (método dos maiores restos)."""
    soma = sum(materias.values())
    base = {m: horas_totais * p // soma for m, p in materias.items()}
    resto = horas_totais - sum(base.values())
    ordem = sorted(materias, key=lambda m: (-(horas_totais * materias[m] % soma), m))
    for m in ordem[:resto]:
        base[m] += 1
    return base


def montar(materias: Dict[str, int], inicio: date, dias: int, horas_dia: int) -> List[Tuple[date, str, int]]:
    horas = distribuir(materias, dias * horas_dia)
    fila = [m for m in sorted(materias, key=lambda m: (-horas[m], m)) for _ in range(horas[m])]
    plano: List[Tuple[date, str, int]] = []
    for d in range(dias):
        bloco = fila[d * horas_dia:(d + 1) * horas_dia]
        dia = inicio + timedelta(days=d)
        for m in dict.fromkeys(bloco):
            plano.append((dia, m, bloco.count(m)))
    return plano


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gera cronograma de estudos.")
    p.add_argument("materias", nargs="+", help="formato materia:peso (peso opcional, padrão 1)")
    p.add_argument("--inicio", default=date.today().isoformat())
    p.add_argument("--dias", type=int, default=7)
    p.add_argument("--horas-dia", type=int, default=2)
    a = p.parse_args(argv)
    try:
        materias: Dict[str, int] = {}
        for item in a.materias:
            nome, _, peso = item.partition(":")
            materias[nome] = int(peso) if peso else 1
        if a.dias < 1 or a.horas_dia < 1 or any(v < 1 for v in materias.values()):
            raise ValueError("dias, horas e pesos devem ser positivos")
        inicio = date.fromisoformat(a.inicio)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    for dia, m, h in montar(materias, inicio, a.dias, a.horas_dia):
        print(f"{dia.isoformat()} {m} {h}h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
