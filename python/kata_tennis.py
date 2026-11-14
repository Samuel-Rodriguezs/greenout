"""Tennis Kata: placar de um game de tênis."""
from __future__ import annotations

_NOMES = ["Love", "Fifteen", "Thirty", "Forty"]


def placar(pontos_a: int, pontos_b: int) -> str:
    """Retorna o placar falado dado os pontos dos jogadores A e B."""
    if pontos_a < 0 or pontos_b < 0:
        raise ValueError("pontos não podem ser negativos")
    if pontos_a >= 4 or pontos_b >= 4:
        diff = pontos_a - pontos_b
        if diff == 0:
            return "Deuce"
        if abs(diff) == 1:
            return "Advantage A" if diff > 0 else "Advantage B"
        return "Win for A" if diff > 0 else "Win for B"
    if pontos_a == pontos_b:
        return "Deuce" if pontos_a == 3 else f"{_NOMES[pontos_a]}-All"
    return f"{_NOMES[pontos_a]}-{_NOMES[pontos_b]}"


class Jogo:
    """Acompanha um game ponto a ponto."""

    def __init__(self) -> None:
        self.pontos = {"A": 0, "B": 0}

    def ponto(self, jogador: str) -> None:
        if jogador not in self.pontos:
            raise ValueError("jogador deve ser 'A' ou 'B'")
        if self.terminou():
            raise ValueError("o game já terminou")
        self.pontos[jogador] += 1

    def terminou(self) -> bool:
        return placar(self.pontos["A"], self.pontos["B"]).startswith("Win")

    def placar(self) -> str:
        return placar(self.pontos["A"], self.pontos["B"])
