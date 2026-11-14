"""Câmera 2D com seguimento suave (independente de taxa de quadros), zona morta, limites e tremor."""
from __future__ import annotations

import random
from math import exp


class Camera:
    def __init__(
        self,
        largura: float,
        altura: float,
        limites: tuple[float, float, float, float] | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """`x`,`y` = canto superior esquerdo da vista. `limites` = (x0, y0, x1, y1) do mundo."""
        if largura <= 0 or altura <= 0:
            raise ValueError("viewport deve ser positivo")
        self.largura = largura
        self.altura = altura
        self.x = 0.0
        self.y = 0.0
        self.limites = limites
        self._rng = rng or random.Random(0)
        self._tremor_amp = 0.0
        self._tremor_resta = 0.0
        self._tremor_dur = 0.0
        self.desloc_x = 0.0
        self.desloc_y = 0.0

    @property
    def centro(self) -> tuple[float, float]:
        return (self.x + self.largura / 2, self.y + self.altura / 2)

    def centralizar(self, alvo_x: float, alvo_y: float) -> None:
        self.x = alvo_x - self.largura / 2
        self.y = alvo_y - self.altura / 2
        self._limitar()

    def seguir(
        self,
        alvo_x: float,
        alvo_y: float,
        dt: float,
        velocidade: float = 5.0,
        zona_morta: tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Aproxima o centro do alvo com suavização exponencial.

        fator = 1 - exp(-velocidade * dt): dois passos de dt/2 equivalem a um de dt.
        Dentro da zona morta (meia-largura, meia-altura) a câmera não se move.
        """
        if dt < 0:
            raise ValueError("dt não pode ser negativo")
        cx, cy = self.centro
        dx, dy = alvo_x - cx, alvo_y - cy
        zx, zy = zona_morta
        dx = dx - zx if dx > zx else dx + zx if dx < -zx else 0.0
        dy = dy - zy if dy > zy else dy + zy if dy < -zy else 0.0
        f = 1.0 - exp(-velocidade * dt)
        self.x += dx * f
        self.y += dy * f
        self._limitar()
        self._atualizar_tremor(dt)

    def _limitar(self) -> None:
        if self.limites is None:
            return
        x0, y0, x1, y1 = self.limites
        # mundo menor que a vista: centraliza
        self.x = (x0 + x1 - self.largura) / 2 if x1 - x0 <= self.largura else min(max(self.x, x0), x1 - self.largura)
        self.y = (y0 + y1 - self.altura) / 2 if y1 - y0 <= self.altura else min(max(self.y, y0), y1 - self.altura)

    def tremer(self, amplitude: float, duracao: float) -> None:
        self._tremor_amp = amplitude
        self._tremor_resta = self._tremor_dur = duracao

    def _atualizar_tremor(self, dt: float) -> None:
        if self._tremor_resta <= 0:
            self.desloc_x = self.desloc_y = 0.0
            return
        self._tremor_resta = max(0.0, self._tremor_resta - dt)
        amp = self._tremor_amp * (self._tremor_resta / self._tremor_dur)  # decai linearmente
        self.desloc_x = self._rng.uniform(-amp, amp)
        self.desloc_y = self._rng.uniform(-amp, amp)

    def mundo_para_tela(self, px: float, py: float) -> tuple[float, float]:
        return (px - self.x - self.desloc_x, py - self.y - self.desloc_y)

    def tela_para_mundo(self, sx: float, sy: float) -> tuple[float, float]:
        return (sx + self.x + self.desloc_x, sy + self.y + self.desloc_y)

    def visivel(self, px: float, py: float, w: float = 0.0, h: float = 0.0) -> bool:
        return (px <= self.x + self.largura and px + w >= self.x
                and py <= self.y + self.altura and py + h >= self.y)
