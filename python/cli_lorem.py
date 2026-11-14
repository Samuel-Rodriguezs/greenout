"""Gerador de lorem ipsum com seed opcional."""
import argparse
import random
import sys
from typing import List, Optional, Sequence

PALAVRAS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore "
    "magna aliqua enim ad minim veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
    "consequat duis aute irure in reprehenderit voluptate velit esse cillum fugiat nulla pariatur"
).split()


def frase(rng: random.Random, min_pal: int = 6, max_pal: int = 14) -> str:
    n = rng.randint(min_pal, max_pal)
    texto = " ".join(rng.choice(PALAVRAS) for _ in range(n))
    return texto.capitalize() + "."


def paragrafo(rng: random.Random, frases: int = 4) -> str:
    return " ".join(frase(rng) for _ in range(frases))


def gerar(paragrafos: int, seed: Optional[int] = None) -> List[str]:
    rng = random.Random(seed)
    ps = [paragrafo(rng, rng.randint(3, 6)) for _ in range(paragrafos)]
    if ps:
        ps[0] = "Lorem ipsum dolor sit amet. " + ps[0]
    return ps


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gera texto lorem ipsum.")
    p.add_argument("-p", "--paragrafos", type=int, default=3)
    p.add_argument("--seed", type=int)
    p.add_argument("--palavras", type=int, help="limita a saída a N palavras")
    a = p.parse_args(argv)
    if a.paragrafos < 1:
        print("erro: paragrafos deve ser >= 1", file=sys.stderr)
        return 1
    texto = "\n\n".join(gerar(a.paragrafos, a.seed))
    if a.palavras:
        texto = " ".join(texto.split()[: a.palavras])
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
