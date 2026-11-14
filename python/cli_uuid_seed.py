"""Gerador de UUIDs (versão 4) determinísticos a partir de uma seed."""
import argparse
import random
import sys
import uuid
from typing import List, Optional, Sequence


def gerar_uuids(seed: int, quantidade: int) -> List[str]:
    rng = random.Random(seed)
    return [str(uuid.UUID(int=rng.getrandbits(128), version=4)) for _ in range(quantidade)]


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gera UUIDs determinísticos por seed.")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("-n", "--quantidade", type=int, default=1)
    p.add_argument("--maiusculas", action="store_true")
    a = p.parse_args(argv)
    if a.quantidade < 1:
        print("erro: quantidade deve ser >= 1", file=sys.stderr)
        return 1
    for u in gerar_uuids(a.seed, a.quantidade):
        print(u.upper() if a.maiusculas else u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
