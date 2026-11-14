"""Elevador com algoritmo SCAN (varre em uma direção antes de inverter)."""
from __future__ import annotations


class Elevador:
    def __init__(self, andares: int = 10, capacidade: int = 8, andar_inicial: int = 0) -> None:
        if not 0 <= andar_inicial < andares:
            raise ValueError("andar inicial inválido")
        self.andares = andares
        self.capacidade = capacidade
        self.andar = andar_inicial
        self.direcao = 1
        self.espera: list[tuple[int, int]] = []  # (origem, destino)
        self.dentro: list[int] = []  # destinos dos passageiros a bordo
        self.entregues = 0
        self.tempo = 0

    def chamar(self, origem: int, destino: int) -> None:
        for a in (origem, destino):
            if not 0 <= a < self.andares:
                raise ValueError("andar inexistente")
        if origem == destino:
            raise ValueError("origem e destino iguais")
        self.espera.append((origem, destino))

    def _paradas(self) -> set[int]:
        return set(self.dentro) | {o for o, _ in self.espera}

    @property
    def ocioso(self) -> bool:
        return not self.dentro and not self.espera

    def _trocar_passageiros(self) -> None:
        saindo = [d for d in self.dentro if d == self.andar]
        self.dentro = [d for d in self.dentro if d != self.andar]
        self.entregues += len(saindo)
        ficam = []
        for o, d in self.espera:
            if o == self.andar and len(self.dentro) < self.capacidade:
                self.dentro.append(d)
            else:
                ficam.append((o, d))
        self.espera = ficam

    def passo(self) -> None:
        """Uma unidade de tempo: atende o andar atual e então move um andar."""
        self.tempo += 1
        self._trocar_passageiros()
        paradas = self._paradas()
        if not paradas:
            return
        acima = any(p > self.andar for p in paradas)
        abaixo = any(p < self.andar for p in paradas)
        if self.direcao == 1 and not acima:
            self.direcao = -1
        elif self.direcao == -1 and not abaixo:
            self.direcao = 1
        if (self.direcao == 1 and acima) or (self.direcao == -1 and abaixo):
            self.andar += self.direcao
        elif acima or abaixo:
            self.direcao = -self.direcao
            self.andar += self.direcao

    def executar_ate_ocioso(self, limite: int = 10000) -> int:
        n = 0
        while not self.ocioso and n < limite:
            self.passo()
            n += 1
        if not self.ocioso:
            raise RuntimeError("limite de passos excedido")
        self._trocar_passageiros()
        return n
