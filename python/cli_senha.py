"""Gerador de senhas com seed opcional para resultados reproduzíveis."""
import argparse
import random
import string
import sys
from typing import List, Optional, Sequence


def gerar_senha(tamanho: int, rng: random.Random, simbolos: bool = True) -> str:
    if tamanho < 4:
        raise ValueError("tamanho mínimo é 4")
    grupos = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if simbolos:
        grupos.append("!@#$%&*?")
    chars: List[str] = [rng.choice(g) for g in grupos]
    todos = "".join(grupos)
    chars += [rng.choice(todos) for _ in range(tamanho - len(chars))]
    rng.shuffle(chars)
    return "".join(chars)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gera senhas aleatórias.")
    p.add_argument("-t", "--tamanho", type=int, default=12)
    p.add_argument("-n", "--quantidade", type=int, default=1)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--sem-simbolos", action="store_true")
    a = p.parse_args(argv)
    rng = random.Random(a.seed)
    try:
        for _ in range(a.quantidade):
            print(gerar_senha(a.tamanho, rng, not a.sem_simbolos))
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
