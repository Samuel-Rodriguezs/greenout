"""Sorteador de itens, ordem e times, com seed opcional."""
import argparse
import random
import sys
from typing import List, Optional, Sequence


def sortear(itens: Sequence[str], quantidade: int, rng: random.Random) -> List[str]:
    if not 1 <= quantidade <= len(itens):
        raise ValueError("quantidade deve estar entre 1 e o número de itens")
    return rng.sample(list(itens), quantidade)


def dividir_times(itens: Sequence[str], times: int, rng: random.Random) -> List[List[str]]:
    if not 1 <= times <= len(itens):
        raise ValueError("número de times inválido")
    emb = list(itens)
    rng.shuffle(emb)
    return [emb[i::times] for i in range(times)]


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Sorteia itens ou divide em times.")
    p.add_argument("itens", nargs="+")
    p.add_argument("-n", "--quantidade", type=int, default=1)
    p.add_argument("--times", type=int, help="divide os itens em N times")
    p.add_argument("--seed", type=int)
    a = p.parse_args(argv)
    rng = random.Random(a.seed)
    try:
        if a.times:
            for i, t in enumerate(dividir_times(a.itens, a.times, rng), 1):
                print(f"Time {i}: {', '.join(t)}")
        else:
            for item in sortear(a.itens, a.quantidade, rng):
                print(item)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
