"""Barramento de eventos com prioridade, filas e assinaturas de uso único."""
from __future__ import annotations

from typing import Any, Callable

Ouvinte = Callable[[Any], None]


class BarramentoEventos:
    def __init__(self) -> None:
        self._ouvintes: dict[str, list[tuple[int, int, Ouvinte, bool]]] = {}
        self._fila: list[tuple[str, Any]] = []
        self._seq = 0

    def assinar(self, topico: str, fn: Ouvinte, prioridade: int = 0, uma_vez: bool = False) -> Callable[[], None]:
        """Registra `fn`; maior prioridade roda primeiro. Devolve função de cancelamento."""
        item = (-prioridade, self._seq, fn, uma_vez)
        self._seq += 1
        lista = self._ouvintes.setdefault(topico, [])
        lista.append(item)
        lista.sort(key=lambda i: (i[0], i[1]))

        def cancelar() -> None:
            if item in self._ouvintes.get(topico, []):
                self._ouvintes[topico].remove(item)

        return cancelar

    def publicar(self, topico: str, dados: Any = None) -> int:
        """Entrega imediatamente; devolve quantos ouvintes receberam."""
        entregues = 0
        for item in list(self._ouvintes.get(topico, [])):
            if item not in self._ouvintes.get(topico, []):
                continue  # cancelado por um ouvinte anterior
            if item[3]:
                self._ouvintes[topico].remove(item)
            item[2](dados)
            entregues += 1
        return entregues

    def enfileirar(self, topico: str, dados: Any = None) -> None:
        self._fila.append((topico, dados))

    def despachar(self) -> int:
        """Entrega eventos enfileirados (inclusive os enfileirados durante o despacho)."""
        total = 0
        while self._fila:
            topico, dados = self._fila.pop(0)
            self.publicar(topico, dados)
            total += 1
        return total

    def quantidade(self, topico: str) -> int:
        return len(self._ouvintes.get(topico, []))
