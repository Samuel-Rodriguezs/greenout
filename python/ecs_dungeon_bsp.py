"""Geração de dungeon por partição binária do espaço (BSP) com seed (1 = parede, 0 = chão)."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

Grade = list[list[int]]


@dataclass(frozen=True)
class Sala:
    x: int
    y: int
    w: int
    h: int

    @property
    def centro(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


@dataclass
class _No:
    x: int
    y: int
    w: int
    h: int
    esq: "_No | None" = None
    dir: "_No | None" = None
    sala: Sala | None = field(default=None)


def _dividir(no: _No, rng: random.Random, min_folha: int) -> None:
    pode_h = no.w >= 2 * min_folha  # corte vertical
    pode_v = no.h >= 2 * min_folha  # corte horizontal
    if not pode_h and not pode_v:
        return
    if pode_h and pode_v:
        if no.w > no.h * 1.25:
            vertical = True
        elif no.h > no.w * 1.25:
            vertical = False
        else:
            vertical = rng.random() < 0.5
    else:
        vertical = pode_h
    if vertical:
        c = rng.randint(min_folha, no.w - min_folha)
        no.esq = _No(no.x, no.y, c, no.h)
        no.dir = _No(no.x + c, no.y, no.w - c, no.h)
    else:
        c = rng.randint(min_folha, no.h - min_folha)
        no.esq = _No(no.x, no.y, no.w, c)
        no.dir = _No(no.x, no.y + c, no.w, no.h - c)
    _dividir(no.esq, rng, min_folha)
    _dividir(no.dir, rng, min_folha)


def _folhas(no: _No) -> list[_No]:
    if no.esq is None:
        return [no]
    return _folhas(no.esq) + _folhas(no.dir)  # type: ignore[arg-type]


def _escavar(g: Grade, x: int, y: int, w: int, h: int) -> None:
    for j in range(y, y + h):
        for i in range(x, x + w):
            g[j][i] = 0


def _sala_representante(no: _No) -> Sala:
    while no.sala is None:
        no = no.esq  # type: ignore[assignment]
    return no.sala


def _corredor(g: Grade, a: tuple[int, int], b: tuple[int, int], rng: random.Random) -> None:
    (x1, y1), (x2, y2) = a, b
    if rng.random() < 0.5:
        _escavar(g, min(x1, x2), y1, abs(x2 - x1) + 1, 1)
        _escavar(g, x2, min(y1, y2), 1, abs(y2 - y1) + 1)
    else:
        _escavar(g, x1, min(y1, y2), 1, abs(y2 - y1) + 1)
        _escavar(g, min(x1, x2), y2, abs(x2 - x1) + 1, 1)


def _ligar(no: _No, g: Grade, rng: random.Random) -> None:
    if no.esq is None:
        return
    _ligar(no.esq, g, rng)
    _ligar(no.dir, g, rng)  # type: ignore[arg-type]
    a = _sala_representante(no.esq).centro
    b = _sala_representante(no.dir).centro  # type: ignore[arg-type]
    _corredor(g, a, b, rng)
    no.sala = _sala_representante(no.esq)


def gerar(
    largura: int,
    altura: int,
    seed: int,
    min_sala: int = 4,
) -> tuple[Grade, list[Sala]]:
    """Devolve (grade, salas). Cada folha da BSP recebe uma sala com margem de 1 célula."""
    if min_sala < 3:
        raise ValueError("min_sala deve ser >= 3")
    min_folha = min_sala + 2
    if largura < min_folha or altura < min_folha:
        raise ValueError("mapa pequeno demais para uma sala")
    rng = random.Random(seed)
    raiz = _No(0, 0, largura, altura)
    _dividir(raiz, rng, min_folha)
    g: Grade = [[1] * largura for _ in range(altura)]
    salas: list[Sala] = []
    for folha in _folhas(raiz):
        w = rng.randint(min_sala, folha.w - 2)
        h = rng.randint(min_sala, folha.h - 2)
        x = folha.x + rng.randint(1, folha.w - w - 1)
        y = folha.y + rng.randint(1, folha.h - h - 1)
        folha.sala = Sala(x, y, w, h)
        salas.append(folha.sala)
        _escavar(g, x, y, w, h)
    _ligar(raiz, g, rng)
    return g, salas
