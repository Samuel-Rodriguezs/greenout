"""Torre de Hanói interativa: estado, validação de jogadas e dicas."""
from __future__ import annotations


class HanoiJogo:
    def __init__(self, discos: int = 3) -> None:
        if discos < 1:
            raise ValueError("precisa de ao menos 1 disco")
        self.discos = discos
        self.pinos: list[list[int]] = [list(range(discos, 0, -1)), [], []]
        self.jogadas = 0

    @property
    def minimo(self) -> int:
        return 2 ** self.discos - 1

    def mover(self, origem: int, destino: int) -> None:
        for p in (origem, destino):
            if not 0 <= p < 3:
                raise ValueError("pino inválido")
        if origem == destino:
            raise ValueError("origem e destino iguais")
        if not self.pinos[origem]:
            raise ValueError("pino de origem vazio")
        disco = self.pinos[origem][-1]
        if self.pinos[destino] and self.pinos[destino][-1] < disco:
            raise ValueError("disco maior sobre menor")
        self.pinos[destino].append(self.pinos[origem].pop())
        self.jogadas += 1

    @property
    def venceu(self) -> bool:
        return len(self.pinos[2]) == self.discos

    def dica(self) -> tuple[int, int] | None:
        """Próxima jogada ótima a partir do estado atual (resolve rumo ao pino 2)."""
        return _proxima(self.pinos, self.discos, 2)


def _proxima(pinos: list[list[int]], n: int, alvo: int) -> tuple[int, int] | None:
    """Próximo movimento para levar os discos 1..n ao pino alvo."""
    if n == 0:
        return None
    pos = next(i for i in range(3) if n in pinos[i])
    if pos == alvo:
        return _proxima(pinos, n - 1, alvo)
    auxiliar = 3 - pos - alvo
    # discos menores precisam estar no auxiliar antes de mover n
    if any(d < n for d in pinos[pos]) or any(d < n for d in pinos[alvo]):
        return _proxima(pinos, n - 1, auxiliar)
    return (pos, alvo)
