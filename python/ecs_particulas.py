"""Física de partículas 2D com gravidade e atrito (Euler semi-implícito)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Particula:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    massa: float = 1.0
    fx: float = 0.0  # força acumulada no quadro
    fy: float = 0.0

    def aplicar_forca(self, fx: float, fy: float) -> None:
        self.fx += fx
        self.fy += fy


def passo(
    p: Particula,
    dt: float,
    gravidade: tuple[float, float] = (0.0, 9.8),
    atrito_linear: float = 0.0,
) -> None:
    """Avança `dt`: atualiza velocidade primeiro e só então a posição.

    `atrito_linear` é o coeficiente c de arrasto F = -c * v (aplicado de forma
    implícita para ficar estável mesmo com c*dt grande).
    """
    if dt < 0:
        raise ValueError("dt não pode ser negativo")
    if p.massa <= 0:
        raise ValueError("massa deve ser positiva")
    ax = p.fx / p.massa + gravidade[0]
    ay = p.fy / p.massa + gravidade[1]
    p.vx += ax * dt
    p.vy += ay * dt
    if atrito_linear:
        fator = 1.0 / (1.0 + atrito_linear / p.massa * dt)
        p.vx *= fator
        p.vy *= fator
    p.x += p.vx * dt
    p.y += p.vy * dt
    p.fx = p.fy = 0.0


def quicar_no_chao(p: Particula, y_chao: float, restituicao: float = 0.5, atrito_solo: float = 0.0) -> bool:
    """Colide com um chão horizontal em y_chao (eixo y cresce para baixo)."""
    if p.y <= y_chao:
        return False
    p.y = y_chao
    if p.vy > 0:
        p.vy = -p.vy * restituicao
    p.vx *= max(0.0, 1.0 - atrito_solo)
    return True


def simular(p: Particula, passos: int, dt: float, **kw) -> list[tuple[float, float]]:
    """Trajetória após cada passo."""
    traj = []
    for _ in range(passos):
        passo(p, dt, **kw)
        traj.append((p.x, p.y))
    return traj
