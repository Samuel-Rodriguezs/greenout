"""Simulação de fila de banco (eventos discretos por minuto, múltiplos caixas)."""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass


@dataclass
class Resultado:
    atendidos: int
    espera_media: float
    espera_maxima: int
    fila_maxima: int
    ocupacao: float  # fração média de caixas ocupados


def simular(minutos: int, caixas: int, prob_chegada: float, tempo_medio_atendimento: int,
            rng: random.Random) -> Resultado:
    """Chegada de Bernoulli por minuto; atendimento uniforme em [1, 2*media-1]."""
    if caixas < 1 or minutos < 1:
        raise ValueError("caixas e minutos devem ser positivos")
    if not 0 <= prob_chegada <= 1:
        raise ValueError("probabilidade inválida")
    if tempo_medio_atendimento < 1:
        raise ValueError("tempo médio inválido")
    fila: deque[int] = deque()  # instante de chegada
    livres_em = [0] * caixas  # minuto em que cada caixa fica livre
    esperas: list[int] = []
    fila_max = 0
    ocupados_total = 0
    for t in range(minutos):
        if rng.random() < prob_chegada:
            fila.append(t)
        for i in range(caixas):
            if livres_em[i] <= t and fila:
                chegada = fila.popleft()
                esperas.append(t - chegada)
                livres_em[i] = t + rng.randint(1, 2 * tempo_medio_atendimento - 1)
        fila_max = max(fila_max, len(fila))
        ocupados_total += sum(1 for x in livres_em if x > t)
    return Resultado(
        atendidos=len(esperas),
        espera_media=sum(esperas) / len(esperas) if esperas else 0.0,
        espera_maxima=max(esperas, default=0),
        fila_maxima=fila_max,
        ocupacao=ocupados_total / (minutos * caixas),
    )
