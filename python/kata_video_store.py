"""Video Store Kata (Fowler): extrato de aluguéis com valores e pontos de fidelidade."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Categoria(Enum):
    REGULAR = "regular"
    LANCAMENTO = "lancamento"
    INFANTIL = "infantil"


@dataclass(frozen=True)
class Filme:
    titulo: str
    categoria: Categoria


@dataclass(frozen=True)
class Aluguel:
    filme: Filme
    dias: int

    def __post_init__(self) -> None:
        if self.dias < 1:
            raise ValueError("dias deve ser >= 1")

    def valor(self) -> float:
        cat = self.filme.categoria
        if cat is Categoria.REGULAR:
            return 2.0 + max(0, self.dias - 2) * 1.5
        if cat is Categoria.LANCAMENTO:
            return self.dias * 3.0
        return 1.5 + max(0, self.dias - 3) * 1.5

    def pontos(self) -> int:
        if self.filme.categoria is Categoria.LANCAMENTO and self.dias > 1:
            return 2
        return 1


@dataclass
class Cliente:
    nome: str
    alugueis: list[Aluguel] = field(default_factory=list)

    def alugar(self, filme: Filme, dias: int) -> None:
        self.alugueis.append(Aluguel(filme, dias))

    def total(self) -> float:
        return sum(a.valor() for a in self.alugueis)

    def pontos(self) -> int:
        return sum(a.pontos() for a in self.alugueis)

    def extrato(self) -> str:
        linhas = [f"Extrato de aluguel para {self.nome}"]
        for a in self.alugueis:
            linhas.append(f"\t{a.filme.titulo}\t{a.valor():.1f}")
        linhas.append(f"Valor devido: {self.total():.1f}")
        linhas.append(f"Você ganhou {self.pontos()} pontos de fidelidade")
        return "\n".join(linhas)
