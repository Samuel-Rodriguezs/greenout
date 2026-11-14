"""Rolagem de dados de RPG: parser de notação como '2d6+3', '4d6kh3', '1d20-1'."""
from __future__ import annotations

import random
import re
from dataclasses import dataclass

_PADRAO = re.compile(r"^\s*(\d*)d(\d+)(?:(kh|kl)(\d+))?\s*(?:([+-])\s*(\d+))?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Expressao:
    quantidade: int
    faces: int
    manter: str | None  # 'kh' (maiores) ou 'kl' (menores)
    n_manter: int
    modificador: int


@dataclass(frozen=True)
class Rolagem:
    expressao: Expressao
    dados: tuple[int, ...]
    mantidos: tuple[int, ...]
    total: int


def parse(texto: str) -> Expressao:
    m = _PADRAO.match(texto)
    if not m:
        raise ValueError(f"expressão inválida: {texto!r}")
    qtd = int(m.group(1)) if m.group(1) else 1
    faces = int(m.group(2))
    if qtd < 1 or qtd > 1000 or faces < 2:
        raise ValueError("quantidade ou faces fora do intervalo")
    manter = m.group(3).lower() if m.group(3) else None
    n_manter = int(m.group(4)) if m.group(4) else 0
    if manter and not 1 <= n_manter <= qtd:
        raise ValueError("quantidade de dados mantidos inválida")
    mod = int(m.group(6)) if m.group(6) else 0
    if m.group(5) == "-":
        mod = -mod
    return Expressao(qtd, faces, manter, n_manter, mod)


def rolar(texto: str, rng: random.Random) -> Rolagem:
    e = parse(texto)
    dados = tuple(rng.randint(1, e.faces) for _ in range(e.quantidade))
    if e.manter == "kh":
        mantidos = tuple(sorted(dados, reverse=True)[:e.n_manter])
    elif e.manter == "kl":
        mantidos = tuple(sorted(dados)[:e.n_manter])
    else:
        mantidos = dados
    return Rolagem(e, dados, mantidos, sum(mantidos) + e.modificador)


def intervalo(texto: str) -> tuple[int, int]:
    """Mínimo e máximo possíveis para a expressão."""
    e = parse(texto)
    n = e.n_manter if e.manter else e.quantidade
    return n + e.modificador, n * e.faces + e.modificador


def media(texto: str) -> float:
    """Média teórica (somente sem 'keep')."""
    e = parse(texto)
    if e.manter:
        raise ValueError("média teórica não suportada com keep")
    return e.quantidade * (e.faces + 1) / 2 + e.modificador
