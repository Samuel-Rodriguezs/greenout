"""Relógio mundial com offsets UTC fixos (sem horário de verão)."""
import argparse
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Sequence

CIDADES: Dict[str, float] = {
    "brasilia": -3,
    "nova-york": -5,
    "los-angeles": -8,
    "londres": 0,
    "paris": 1,
    "moscou": 3,
    "dubai": 4,
    "nova-delhi": 5.5,
    "pequim": 8,
    "toquio": 9,
    "sydney": 10,
}


def hora_em(utc: datetime, cidade: str) -> datetime:
    if cidade not in CIDADES:
        raise ValueError(f"cidade desconhecida: {cidade}")
    return utc.astimezone(timezone(timedelta(hours=CIDADES[cidade])))


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Mostra a hora em várias cidades.")
    p.add_argument("cidades", nargs="*", help="padrão: todas")
    p.add_argument("--utc", help="instante UTC AAAA-MM-DDTHH:MM (padrão: agora)")
    a = p.parse_args(argv)
    try:
        utc = datetime.fromisoformat(a.utc).replace(tzinfo=timezone.utc) if a.utc else datetime.now(timezone.utc)
        for c in a.cidades or sorted(CIDADES):
            h = hora_em(utc, c)
            print(f"{c}: {h:%Y-%m-%d %H:%M} (UTC{h.strftime('%z')[:3]}:{h.strftime('%z')[3:]})")
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
