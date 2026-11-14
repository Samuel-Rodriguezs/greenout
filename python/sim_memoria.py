"""Jogo da memória (pares de cartas)."""
from __future__ import annotations

import random


class JogoMemoria:
    def __init__(self, simbolos: list[str], rng: random.Random | None = None) -> None:
        if not simbolos or len(set(simbolos)) != len(simbolos):
            raise ValueError("símbolos devem ser únicos e não vazios")
        self.rng = rng or random.Random()
        self.cartas = list(simbolos) * 2
        self.rng.shuffle(self.cartas)
        self.encontradas: set[int] = set()
        self.viradas: list[int] = []
        self.tentativas = 0

    def virar(self, i: int) -> str:
        """Retorna 'primeira', 'par' ou 'erro' conforme o resultado."""
        if not 0 <= i < len(self.cartas):
            raise IndexError("carta inexistente")
        if len(self.viradas) == 2:
            self.viradas = []
        if i in self.encontradas or i in self.viradas:
            raise ValueError("carta indisponível")
        self.viradas.append(i)
        if len(self.viradas) == 1:
            return "primeira"
        self.tentativas += 1
        a, b = self.viradas
        if self.cartas[a] == self.cartas[b]:
            self.encontradas.update(self.viradas)
            self.viradas = []
            return "par"
        return "erro"

    @property
    def terminou(self) -> bool:
        return len(self.encontradas) == len(self.cartas)
