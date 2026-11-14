"""E-mails fictícios derivados de nomes (domínios reservados .example)."""
from __future__ import annotations

import random
import re
import unicodedata

from gen_nomes import PARTICULAS, gerar_nome_completo

DOMINIOS: tuple[str, ...] = ("exemplo.com.br", "teste.example", "correio.example", "mail.example")


def remover_acentos(texto: str) -> str:
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if not unicodedata.combining(c))


def _slug(parte: str) -> str:
    return re.sub(r"[^a-z0-9]", "", remover_acentos(parte).lower())


def email_do_nome(nome: str, rng: random.Random, dominio: str | None = None) -> str:
    """Deriva o e-mail do nome completo, escolhendo um dos estilos de usuário."""
    partes = [_slug(p) for p in nome.split() if p.lower() not in PARTICULAS]
    partes = [p for p in partes if p]
    if not partes:
        raise ValueError("nome sem partes aproveitáveis")
    primeiro, ultimo = partes[0], partes[-1]
    estilos = (
        f"{primeiro}.{ultimo}",
        f"{primeiro}{ultimo}",
        f"{primeiro[0]}{ultimo}",
        f"{primeiro}_{ultimo}{rng.randint(1, 99)}",
    )
    usuario = rng.choice(estilos)
    return f"{usuario}@{dominio or rng.choice(DOMINIOS)}"


def gerar_emails_unicos(rng: random.Random, n: int) -> list[tuple[str, str]]:
    """Pares (nome, e-mail) com e-mails todos distintos (sufixo numérico em colisões)."""
    vistos: set[str] = set()
    saida: list[tuple[str, str]] = []
    while len(saida) < n:
        nome = gerar_nome_completo(rng)
        email = email_do_nome(nome, rng)
        if email in vistos:
            usuario, dom = email.split("@")
            k = 2
            while f"{usuario}{k}@{dom}" in vistos:
                k += 1
            email = f"{usuario}{k}@{dom}"
        vistos.add(email)
        saida.append((nome, email))
    return saida
