"""Loop de jogo com passo fixo (accumulator) e fator de interpolação."""
from __future__ import annotations

from typing import Callable


class LoopPassoFixo:
    """Acumula tempo real e dispara atualizações em passos fixos.

    O tempo é injetado via `avancar(dt_real)`, sem relógio interno.
    """

    def __init__(self, passo: float = 1 / 60, max_passos: int = 5) -> None:
        if passo <= 0:
            raise ValueError("passo deve ser positivo")
        if max_passos < 1:
            raise ValueError("max_passos deve ser >= 1")
        self.passo = passo
        self.max_passos = max_passos
        self.acumulador = 0.0
        self.tempo_simulado = 0.0
        self.passos_totais = 0

    def avancar(self, dt_real: float, atualizar: Callable[[float], None]) -> float:
        """Consome dt_real; devolve alpha em [0,1) para interpolar a renderização.

        Se o acumulado exceder `max_passos` passos (espiral da morte), o
        excedente é descartado.
        """
        if dt_real < 0:
            raise ValueError("dt_real não pode ser negativo")
        self.acumulador += dt_real
        passos = 0
        while self.acumulador >= self.passo - 1e-12 and passos < self.max_passos:
            atualizar(self.passo)
            self.acumulador -= self.passo
            self.tempo_simulado += self.passo
            self.passos_totais += 1
            passos += 1
        if passos == self.max_passos and self.acumulador >= self.passo:
            self.acumulador %= self.passo
        if self.acumulador < 0:
            self.acumulador = 0.0
        return self.acumulador / self.passo


def interpolar(anterior: float, atual: float, alpha: float) -> float:
    """Estado exibido entre dois passos de simulação."""
    return anterior + (atual - anterior) * alpha
