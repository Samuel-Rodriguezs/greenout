"""Enum com comportamento: prioridades ordenáveis e máquina de estados."""
import enum
from typing import FrozenSet


@enum.unique
class Prioridade(enum.IntEnum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3

    @classmethod
    def de_texto(cls, texto: str) -> "Prioridade":
        try:
            return cls[texto.strip().upper()]
        except KeyError:
            raise ValueError(f"prioridade desconhecida: {texto!r}") from None

    def escalar(self) -> "Prioridade":
        return Prioridade(min(self + 1, Prioridade.ALTA))


class Estado(enum.Enum):
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"

    @property
    def proximos(self) -> FrozenSet["Estado"]:
        return _TRANSICOES[self]

    @property
    def final(self) -> bool:
        return not self.proximos

    def transicionar(self, destino: "Estado") -> "Estado":
        if destino not in self.proximos:
            raise ValueError(f"transição inválida: {self.value} -> {destino.value}")
        return destino


_TRANSICOES = {
    Estado.ABERTO: frozenset({Estado.EM_ANDAMENTO, Estado.CANCELADO}),
    Estado.EM_ANDAMENTO: frozenset({Estado.CONCLUIDO, Estado.CANCELADO, Estado.ABERTO}),
    Estado.CONCLUIDO: frozenset(),
    Estado.CANCELADO: frozenset(),
}
