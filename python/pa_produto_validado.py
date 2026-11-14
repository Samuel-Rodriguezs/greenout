"""Dataclass congelada com validação em __post_init__ e ordenação."""
from dataclasses import dataclass, field, replace
from typing import Tuple


@dataclass(frozen=True, order=True)
class Produto:
    nome: str
    preco_centavos: int
    estoque: int = 0
    tags: Tuple[str, ...] = field(default=(), compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome obrigatório")
        if isinstance(self.preco_centavos, bool) or not isinstance(self.preco_centavos, int):
            raise TypeError("preco_centavos deve ser int")
        if self.preco_centavos < 0:
            raise ValueError("preço negativo")
        if self.estoque < 0:
            raise ValueError("estoque negativo")
        object.__setattr__(self, "nome", self.nome.strip())
        object.__setattr__(self, "tags", tuple(self.tags))

    def com_estoque(self, novo: int) -> "Produto":
        return replace(self, estoque=novo)  # revalida via __post_init__

    @property
    def preco(self) -> str:
        return f"R$ {self.preco_centavos // 100},{self.preco_centavos % 100:02d}"
