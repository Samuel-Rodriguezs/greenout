"""Gerenciador de cenas com pilha de estados."""
from __future__ import annotations


class Cena:
    """Cena base; subclasses sobrescrevem os ganchos."""

    #: se True, a cena abaixo também é atualizada (ex.: HUD sobre o jogo)
    transparente_update: bool = False

    def entrar(self) -> None: ...
    def sair(self) -> None: ...
    def pausar(self) -> None: ...
    def retomar(self) -> None: ...
    def atualizar(self, dt: float) -> None: ...


class PilhaCenas:
    def __init__(self) -> None:
        self._pilha: list[Cena] = []

    def __len__(self) -> int:
        return len(self._pilha)

    @property
    def topo(self) -> Cena | None:
        return self._pilha[-1] if self._pilha else None

    def empilhar(self, cena: Cena) -> None:
        if self._pilha:
            self._pilha[-1].pausar()
        self._pilha.append(cena)
        cena.entrar()

    def desempilhar(self) -> Cena:
        if not self._pilha:
            raise IndexError("pilha de cenas vazia")
        cena = self._pilha.pop()
        cena.sair()
        if self._pilha:
            self._pilha[-1].retomar()
        return cena

    def trocar(self, cena: Cena) -> None:
        """Substitui o topo sem retomar a cena abaixo."""
        if self._pilha:
            self._pilha.pop().sair()
        self._pilha.append(cena)
        cena.entrar()

    def atualizar(self, dt: float) -> None:
        """Atualiza o topo e, enquanto transparente, as cenas abaixo."""
        for cena in reversed(list(self._pilha)):
            cena.atualizar(dt)
            if not cena.transparente_update:
                break

    def nomes(self) -> list[str]:
        return [type(c).__name__ for c in self._pilha]
