"""Gerador reprodutível de nomes e sobrenomes brasileiros fictícios."""
from __future__ import annotations

import random

NOMES_MASCULINOS: tuple[str, ...] = (
    "João", "Pedro", "Lucas", "Gabriel", "Mateus", "Rafael", "Bruno", "Carlos",
    "Felipe", "Gustavo", "Henrique", "Thiago", "André", "Marcelo", "Rodrigo",
)
NOMES_FEMININOS: tuple[str, ...] = (
    "Maria", "Ana", "Juliana", "Camila", "Fernanda", "Beatriz", "Larissa",
    "Patrícia", "Aline", "Luciana", "Mariana", "Carolina", "Renata", "Bianca", "Letícia",
)
SOBRENOMES: tuple[str, ...] = (
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Ferreira",
    "Almeida", "Nascimento", "Carvalho", "Ribeiro", "Martins", "Araújo", "Barbosa",
    "Gomes", "Rocha", "Dias", "Moreira", "Cardoso",
)
PARTICULAS: frozenset[str] = frozenset({"da", "de", "do", "dos", "das"})


def gerar_nome(rng: random.Random, genero: str | None = None) -> str:
    """Nome próprio. `genero` é 'M', 'F' ou None (sorteado)."""
    if genero is None:
        genero = rng.choice("MF")
    if genero == "M":
        return rng.choice(NOMES_MASCULINOS)
    if genero == "F":
        return rng.choice(NOMES_FEMININOS)
    raise ValueError("gênero deve ser 'M', 'F' ou None")


def gerar_nome_completo(
    rng: random.Random, genero: str | None = None, n_sobrenomes: int = 2
) -> str:
    """Nome + sobrenomes distintos, às vezes com partícula ('de', 'da')."""
    if n_sobrenomes < 1 or n_sobrenomes > len(SOBRENOMES):
        raise ValueError("n_sobrenomes fora do intervalo válido")
    partes = [gerar_nome(rng, genero)]
    sobrenomes = rng.sample(SOBRENOMES, n_sobrenomes)
    for i, s in enumerate(sobrenomes):
        if i > 0 and rng.random() < 0.3:
            partes.append(rng.choice(sorted(PARTICULAS)))
        partes.append(s)
    return " ".join(partes)


def gerar_lote(rng: random.Random, n: int, genero: str | None = None) -> list[str]:
    return [gerar_nome_completo(rng, genero) for _ in range(n)]
