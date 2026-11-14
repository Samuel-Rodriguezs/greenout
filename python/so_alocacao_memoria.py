"""Alocação contígua de memória: first fit, best fit, worst fit e next fit.

A memória é uma lista de blocos adjacentes (início, tamanho, dono). Liberar um
bloco funde-o com vizinhos livres. `unidade` arredonda os pedidos para cima,
o que produz fragmentação interna mensurável.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

ESTRATEGIAS = ("first", "best", "worst", "next")


class SemMemoria(Exception):
    pass


@dataclass
class Bloco:
    inicio: int
    tamanho: int
    dono: Optional[str] = None  # None = livre
    pedido: int = 0  # bytes realmente pedidos (para a fragmentação interna)

    @property
    def livre(self) -> bool:
        return self.dono is None


class Memoria:
    def __init__(self, tamanho: int, unidade: int = 1) -> None:
        if tamanho <= 0 or unidade <= 0:
            raise ValueError("tamanho e unidade devem ser positivos")
        self.unidade = unidade
        self.blocos = [Bloco(0, tamanho)]
        self._ultimo = 0  # início da última alocação (next fit)

    @classmethod
    def de_blocos(cls, layout: list[tuple[int, Optional[str]]], unidade: int = 1) -> "Memoria":
        """Cria memória a partir de [(tamanho, dono ou None)]; útil para cenários prontos."""
        m = cls(sum(t for t, _ in layout), unidade)
        m.blocos = []
        fim = 0
        for tam, dono in layout:
            m.blocos.append(Bloco(fim, tam, dono, tam if dono else 0))
            fim += tam
        return m

    def _candidatos(self, necessario: int, estrategia: str) -> Optional[Bloco]:
        livres = [b for b in self.blocos if b.livre and b.tamanho >= necessario]
        if not livres:
            return None
        if estrategia == "first":
            return livres[0]
        if estrategia == "best":
            return min(livres, key=lambda b: b.tamanho)  # empate: menor endereço
        if estrategia == "worst":
            return max(livres, key=lambda b: b.tamanho)  # empate: menor endereço
        depois = [b for b in livres if b.inicio >= self._ultimo]
        return (depois or livres)[0]

    def alocar(self, dono: str, tamanho: int, estrategia: str = "first") -> int:
        if estrategia not in ESTRATEGIAS:
            raise ValueError(f"estratégia desconhecida: {estrategia}")
        if tamanho <= 0:
            raise ValueError("tamanho deve ser positivo")
        if any(b.dono == dono for b in self.blocos):
            raise ValueError(f"dono já possui memória: {dono}")
        necessario = -(-tamanho // self.unidade) * self.unidade
        alvo = self._candidatos(necessario, estrategia)
        if alvo is None:
            raise SemMemoria(f"sem lacuna de {necessario} para {dono}")
        resto = alvo.tamanho - necessario
        if resto > 0:
            i = self.blocos.index(alvo)
            self.blocos.insert(i + 1, Bloco(alvo.inicio + necessario, resto))
        alvo.tamanho = necessario
        alvo.dono = dono
        alvo.pedido = tamanho
        self._ultimo = alvo.inicio
        return alvo.inicio

    def liberar(self, dono: str) -> None:
        for i, b in enumerate(self.blocos):
            if b.dono == dono:
                b.dono, b.pedido = None, 0
                if i + 1 < len(self.blocos) and self.blocos[i + 1].livre:
                    b.tamanho += self.blocos.pop(i + 1).tamanho
                if i > 0 and self.blocos[i - 1].livre:
                    self.blocos[i - 1].tamanho += self.blocos.pop(i).tamanho
                return
        raise KeyError(dono)

    def lacunas(self) -> list[tuple[int, int]]:
        return [(b.inicio, b.tamanho) for b in self.blocos if b.livre]

    def livre_total(self) -> int:
        return sum(t for _, t in self.lacunas())

    def maior_lacuna(self) -> int:
        return max((t for _, t in self.lacunas()), default=0)

    def fragmentacao_externa(self) -> int:
        """Memória livre que não cabe num único pedido: livre total menos a maior lacuna."""
        return self.livre_total() - self.maior_lacuna()

    def fragmentacao_interna(self) -> int:
        return sum(b.tamanho - b.pedido for b in self.blocos if not b.livre)
