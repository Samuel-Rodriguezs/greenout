"""Elevator Kata: controlador com algoritmo de varredura (SCAN / "elevador")."""
from __future__ import annotations


class Elevador:
    def __init__(self, andares: int = 10, andar_inicial: int = 0) -> None:
        if andares < 2:
            raise ValueError("são necessários ao menos 2 andares")
        if not 0 <= andar_inicial < andares:
            raise ValueError("andar inicial inválido")
        self.andares = andares
        self.andar = andar_inicial
        self.direcao = 0  # 1 sobe, -1 desce, 0 parado
        self.paradas: set[int] = set()
        self.porta_aberta = False
        self.historico: list[int] = [andar_inicial]

    def chamar(self, andar: int) -> None:
        if not 0 <= andar < self.andares:
            raise ValueError(f"andar inexistente: {andar}")
        if andar != self.andar or self.direcao != 0:
            self.paradas.add(andar)
        elif not self.porta_aberta:
            self.porta_aberta = True

    def _proximo_destino(self) -> int | None:
        if not self.paradas:
            return None
        acima = [a for a in self.paradas if a > self.andar]
        abaixo = [a for a in self.paradas if a < self.andar]
        if self.direcao >= 0 and acima:
            return min(acima)
        if self.direcao <= 0 and abaixo:
            return max(abaixo)
        if acima:
            return min(acima)
        if abaixo:
            return max(abaixo)
        return self.andar

    def passo(self) -> None:
        """Avança um tick: fecha porta, move um andar e abre a porta se for parada."""
        self.porta_aberta = False
        destino = self._proximo_destino()
        if destino is None:
            self.direcao = 0
            return
        if destino > self.andar:
            self.direcao = 1
            self.andar += 1
        elif destino < self.andar:
            self.direcao = -1
            self.andar -= 1
        self.historico.append(self.andar)
        if self.andar in self.paradas:
            self.paradas.discard(self.andar)
            self.porta_aberta = True
            if not self.paradas:
                self.direcao = 0

    def ocioso(self) -> bool:
        return not self.paradas

    def executar_ate_ocioso(self, limite: int = 1000) -> list[int]:
        for _ in range(limite):
            if self.ocioso():
                break
            self.passo()
        else:
            raise RuntimeError("limite de passos excedido")
        return self.historico
