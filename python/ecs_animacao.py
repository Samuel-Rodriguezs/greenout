"""Animação por quadros sobre uma sprite sheet lógica (sem imagens)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Modo = Literal["loop", "uma_vez", "vai_e_volta"]


@dataclass(frozen=True)
class SpriteSheet:
    colunas: int
    linhas: int
    largura_quadro: int
    altura_quadro: int

    def retangulo(self, indice: int) -> tuple[int, int, int, int]:
        """(x, y, w, h) em pixels do quadro `indice`, contado por linhas."""
        if not 0 <= indice < self.colunas * self.linhas:
            raise IndexError(indice)
        col, lin = indice % self.colunas, indice // self.colunas
        return (col * self.largura_quadro, lin * self.altura_quadro,
                self.largura_quadro, self.altura_quadro)


class Animacao:
    def __init__(self, quadros: list[int], duracao_quadro: float, modo: Modo = "loop") -> None:
        if not quadros:
            raise ValueError("animação sem quadros")
        if duracao_quadro <= 0:
            raise ValueError("duracao_quadro deve ser positiva")
        if modo not in ("loop", "uma_vez", "vai_e_volta"):
            raise ValueError(f"modo inválido: {modo}")
        self.quadros = list(quadros)
        self.duracao_quadro = duracao_quadro
        self.modo = modo
        self.tempo = 0.0

    @property
    def _sequencia(self) -> list[int]:
        q = self.quadros
        if self.modo == "vai_e_volta" and len(q) > 2:
            return q + q[-2:0:-1]
        return q

    @property
    def duracao_total(self) -> float:
        return len(self._sequencia) * self.duracao_quadro

    @property
    def terminou(self) -> bool:
        return self.modo == "uma_vez" and self.tempo >= self.duracao_total

    def avancar(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("dt não pode ser negativo")
        self.tempo += dt
        if self.modo == "uma_vez":
            self.tempo = min(self.tempo, self.duracao_total)
        else:
            self.tempo %= self.duracao_total

    def reiniciar(self) -> None:
        self.tempo = 0.0

    @property
    def quadro(self) -> int:
        seq = self._sequencia
        i = int(self.tempo / self.duracao_quadro + 1e-9)
        return seq[min(i, len(seq) - 1)]
