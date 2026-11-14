"""Bowling Game Kata: pontuação de uma partida de boliche (10 frames)."""
from __future__ import annotations


def pontuar(rolagens: list[int]) -> int:
    """Calcula a pontuação total de uma partida completa."""
    if any(not 0 <= r <= 10 for r in rolagens):
        raise ValueError("cada rolagem deve derrubar de 0 a 10 pinos")
    total = 0
    i = 0
    for _ in range(10):
        if i >= len(rolagens):
            raise ValueError("partida incompleta")
        if rolagens[i] == 10:  # strike
            if i + 2 >= len(rolagens):
                raise ValueError("partida incompleta")
            total += 10 + rolagens[i + 1] + rolagens[i + 2]
            i += 1
        else:
            if i + 1 >= len(rolagens):
                raise ValueError("partida incompleta")
            soma = rolagens[i] + rolagens[i + 1]
            if soma > 10:
                raise ValueError("frame com mais de 10 pinos")
            if soma == 10:  # spare
                if i + 2 >= len(rolagens):
                    raise ValueError("partida incompleta")
                total += 10 + rolagens[i + 2]
            else:
                total += soma
            i += 2
    return total
