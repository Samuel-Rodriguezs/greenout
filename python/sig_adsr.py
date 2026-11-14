"""Envelope ADSR (attack, decay, sustain, release)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ADSR:
    """Tempos em segundos; `sustentacao` é o nível (0..1) mantido enquanto a nota dura."""

    ataque: float
    decaimento: float
    sustentacao: float
    liberacao: float

    def __post_init__(self) -> None:
        if min(self.ataque, self.decaimento, self.liberacao) < 0:
            raise ValueError("tempos não podem ser negativos")
        if not 0 <= self.sustentacao <= 1:
            raise ValueError("sustentação deve estar em [0, 1]")

    def nivel(self, t: float, duracao_nota: float) -> float:
        """Nível do envelope no instante t; a nota é solta em `duracao_nota`."""
        if t < 0:
            return 0.0
        if t >= duracao_nota:
            inicio = self._nivel_antes_da_soltura(duracao_nota)
            if self.liberacao == 0:
                return 0.0
            return max(0.0, inicio * (1 - (t - duracao_nota) / self.liberacao))
        return self._nivel_antes_da_soltura(t)

    def _nivel_antes_da_soltura(self, t: float) -> float:
        if t < self.ataque:
            return t / self.ataque
        t -= self.ataque
        if t < self.decaimento:
            return 1 - (1 - self.sustentacao) * t / self.decaimento
        return self.sustentacao

    def amostras(self, taxa: float, duracao_nota: float) -> list[float]:
        """Envelope amostrado, incluindo a liberação."""
        if taxa <= 0 or duracao_nota < 0:
            raise ValueError("taxa e duração inválidas")
        n = int((duracao_nota + self.liberacao) * taxa)
        return [self.nivel(i / taxa, duracao_nota) for i in range(n)]


def aplicar(x: list[float], env: list[float]) -> list[float]:
    """Multiplica o sinal pelo envelope (cortando no menor tamanho)."""
    return [a * b for a, b in zip(x, env)]
