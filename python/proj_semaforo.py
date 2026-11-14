"""Maquina de estados de um semaforo com duracoes por estado."""
from typing import Dict, List, Tuple

TRANSICOES: Dict[str, str] = {"verde": "amarelo", "amarelo": "vermelho", "vermelho": "verde"}
DURACOES: Dict[str, int] = {"verde": 30, "amarelo": 5, "vermelho": 20}


class Semaforo:
    def __init__(self, estado: str = "vermelho") -> None:
        if estado not in TRANSICOES:
            raise ValueError(f"estado invalido: {estado}")
        self.estado = estado
        self.restante = DURACOES[estado]

    def avancar(self) -> str:
        self.estado = TRANSICOES[self.estado]
        self.restante = DURACOES[self.estado]
        return self.estado

    def tick(self, segundos: int = 1) -> str:
        """Passa o tempo; troca de estado sempre que a duracao se esgota."""
        if segundos < 0:
            raise ValueError("tempo negativo")
        while segundos >= self.restante:
            segundos -= self.restante
            self.avancar()
        self.restante -= segundos
        return self.estado

    def pode_passar(self) -> bool:
        return self.estado == "verde"


def linha_do_tempo(inicial: str, total: int) -> List[Tuple[str, int]]:
    """Lista (estado, segundo de entrada) ao longo de `total` segundos."""
    s = Semaforo(inicial)
    eventos = [(s.estado, 0)]
    t = 0
    while t + s.restante < total:
        t += s.restante
        s.avancar()
        eventos.append((s.estado, t))
    return eventos
