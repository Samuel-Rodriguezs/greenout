"""Proxy: cache e controle de acesso sobre um repositório de documentos."""
from __future__ import annotations

from typing import Protocol


class Armazenamento(Protocol):
    def ler(self, nome: str) -> str: ...


class ArmazenamentoLento:
    def __init__(self, dados: dict[str, str]) -> None:
        self._dados = dados
        self.leituras = 0

    def ler(self, nome: str) -> str:
        self.leituras += 1
        return self._dados[nome]


class ProxyArmazenamento:
    def __init__(self, real: Armazenamento, usuario: str,
                 restritos: set[str] | None = None) -> None:
        self._real = real
        self._usuario = usuario
        self._restritos = restritos or set()
        self._cache: dict[str, str] = {}

    def ler(self, nome: str) -> str:
        if nome in self._restritos and self._usuario != "admin":
            raise PermissionError(f"{self._usuario} não pode ler {nome}")
        if nome not in self._cache:
            self._cache[nome] = self._real.ler(nome)
        return self._cache[nome]
