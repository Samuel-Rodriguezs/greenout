"""Estimativa de pi por Monte Carlo."""
import random


def estimar_pi(amostras: int = 100_000, semente: int = 0) -> float:
    """Fração de pontos aleatórios do quadrado unitário dentro do quarto de círculo, vezes 4."""
    if amostras < 1:
        raise ValueError("amostras deve ser >= 1")
    rng = random.Random(semente)
    dentro = 0
    for _ in range(amostras):
        x, y = rng.random(), rng.random()
        if x * x + y * y <= 1.0:
            dentro += 1
    return 4.0 * dentro / amostras
