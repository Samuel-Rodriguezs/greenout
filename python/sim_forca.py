"""Jogo da forca (lógica apenas)."""
from __future__ import annotations

import random
import unicodedata


def _normalizar(c: str) -> str:
    return unicodedata.normalize("NFD", c).encode("ascii", "ignore").decode().lower()


class Forca:
    def __init__(self, palavra: str, max_erros: int = 6) -> None:
        if not palavra or not palavra.isalpha():
            raise ValueError("palavra inválida")
        self.palavra = palavra.lower()
        self.max_erros = max_erros
        self.acertos: set[str] = set()
        self.erros: list[str] = []

    @classmethod
    def sortear(cls, palavras: list[str], rng: random.Random, max_erros: int = 6) -> "Forca":
        return cls(rng.choice(palavras), max_erros)

    def chutar(self, letra: str) -> bool:
        if len(letra) != 1 or not letra.isalpha():
            raise ValueError("chute deve ser uma letra")
        if self.terminou:
            raise RuntimeError("jogo terminado")
        l = _normalizar(letra)
        if l in self.acertos or l in self.erros:
            return l in self.acertos
        if any(_normalizar(c) == l for c in self.palavra):
            self.acertos.add(l)
            return True
        self.erros.append(l)
        return False

    @property
    def mascara(self) -> str:
        return " ".join(c if _normalizar(c) in self.acertos else "_" for c in self.palavra)

    @property
    def venceu(self) -> bool:
        return all(_normalizar(c) in self.acertos for c in self.palavra)

    @property
    def perdeu(self) -> bool:
        return len(self.erros) >= self.max_erros

    @property
    def terminou(self) -> bool:
        return self.venceu or self.perdeu
