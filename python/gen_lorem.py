"""Texto de preenchimento (lorem ipsum) em português do Brasil, reprodutível por seed."""
from __future__ import annotations

import random

PALAVRAS: tuple[str, ...] = (
    "casa", "tempo", "caminho", "livro", "janela", "cidade", "rio", "manhã", "projeto",
    "cadeira", "estrada", "jardim", "música", "ponte", "história", "mercado", "vento",
    "escola", "noite", "lugar", "amigo", "trabalho", "praia", "semana", "palavra",
    "cozinha", "viagem", "sombra", "ideia", "bairro",
)
ADJETIVOS: tuple[str, ...] = (
    "novo", "antigo", "pequeno", "tranquilo", "simples", "claro", "longo", "útil", "leve", "raro",
)
VERBOS: tuple[str, ...] = (
    "muda", "segue", "revela", "guarda", "cresce", "ilumina", "conecta", "descansa", "surpreende", "acompanha",
)
CONECTIVOS: tuple[str, ...] = ("e", "mas", "porque", "enquanto", "embora", "quando")


def gerar_frase(rng: random.Random, min_palavras: int = 6, max_palavras: int = 14) -> str:
    """Frase capitalizada terminada em ponto, com vírgula antes de conectivos adversativos."""
    if not 2 <= min_palavras <= max_palavras:
        raise ValueError("limites de palavras inválidos")
    alvo = rng.randint(min_palavras, max_palavras)
    partes: list[str] = []
    while len(partes) < alvo:
        orac = [rng.choice(PALAVRAS), rng.choice(ADJETIVOS), rng.choice(VERBOS)]
        partes.extend(orac)
        if len(partes) < alvo:
            partes.append(rng.choice(CONECTIVOS))
    partes = partes[:alvo]
    while partes[-1] in CONECTIVOS:
        partes.pop()
    texto = " ".join(partes)
    texto = texto.replace(" mas ", ", mas ").replace(" embora ", ", embora ")
    return texto[0].upper() + texto[1:] + "."


def gerar_paragrafo(rng: random.Random, n_frases: int | None = None) -> str:
    n = n_frases if n_frases is not None else rng.randint(3, 6)
    if n < 1:
        raise ValueError("n_frases deve ser >= 1")
    return " ".join(gerar_frase(rng) for _ in range(n))


def gerar_texto(seed: int, n_paragrafos: int) -> str:
    rng = random.Random(seed)
    return "\n\n".join(gerar_paragrafo(rng) for _ in range(n_paragrafos))


def gerar_palavras(rng: random.Random, n: int) -> list[str]:
    vocab = PALAVRAS + ADJETIVOS + VERBOS
    return [rng.choice(vocab) for _ in range(n)]
