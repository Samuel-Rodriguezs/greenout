"""Agendador de sistemas ordenados por prioridade."""
from __future__ import annotations

from typing import Any, Callable

Sistema = Callable[[Any, float], None]


class Agendador:
    """Executa sistemas em ordem crescente de prioridade (empate: ordem de registro)."""

    def __init__(self) -> None:
        self._itens: list[tuple[int, int, str, Sistema, bool]] = []
        self._seq = 0

    def registrar(self, nome: str, fn: Sistema, prioridade: int = 0) -> None:
        if any(i[2] == nome for i in self._itens):
            raise ValueError(f"sistema já registrado: {nome}")
        self._itens.append((prioridade, self._seq, nome, fn, True))
        self._seq += 1
        self._itens.sort(key=lambda i: (i[0], i[1]))

    def remover(self, nome: str) -> None:
        novos = [i for i in self._itens if i[2] != nome]
        if len(novos) == len(self._itens):
            raise KeyError(nome)
        self._itens = novos

    def habilitar(self, nome: str, ligado: bool) -> None:
        for k, i in enumerate(self._itens):
            if i[2] == nome:
                self._itens[k] = (i[0], i[1], i[2], i[3], ligado)
                return
        raise KeyError(nome)

    def ordem(self) -> list[str]:
        return [i[2] for i in self._itens]

    def executar(self, mundo: Any, dt: float) -> list[str]:
        """Roda os sistemas habilitados e devolve os nomes executados."""
        rodados: list[str] = []
        for _, _, nome, fn, ligado in list(self._itens):
            if ligado:
                fn(mundo, dt)
                rodados.append(nome)
        return rodados
