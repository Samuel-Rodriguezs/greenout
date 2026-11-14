"""Strategy: cálculo de frete com estratégias intercambiáveis."""
from __future__ import annotations

from typing import Callable

EstrategiaFrete = Callable[[float, float], float]  # (peso_kg, distancia_km)


def frete_economico(peso: float, distancia: float) -> float:
    return round(5 + 0.02 * peso * distancia, 2)


def frete_expresso(peso: float, distancia: float) -> float:
    return round(15 + 0.05 * peso * distancia, 2)


def frete_gratis_acima(minimo_kg: float, base: EstrategiaFrete) -> EstrategiaFrete:
    def estrategia(peso: float, distancia: float) -> float:
        return 0.0 if peso >= minimo_kg else base(peso, distancia)
    return estrategia


class Pedido:
    def __init__(self, peso: float, distancia: float, estrategia: EstrategiaFrete) -> None:
        self.peso = peso
        self.distancia = distancia
        self.estrategia = estrategia

    def frete(self) -> float:
        return self.estrategia(self.peso, self.distancia)
