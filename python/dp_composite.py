"""Composite: sistema de arquivos com arquivos e diretórios."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class No(ABC):
    def __init__(self, nome: str) -> None:
        self.nome = nome

    @abstractmethod
    def tamanho(self) -> int: ...

    @abstractmethod
    def listar(self, prefixo: str = "") -> Iterator[str]: ...


class Arquivo(No):
    def __init__(self, nome: str, bytes_: int) -> None:
        super().__init__(nome)
        self.bytes_ = bytes_

    def tamanho(self) -> int:
        return self.bytes_

    def listar(self, prefixo: str = "") -> Iterator[str]:
        yield f"{prefixo}{self.nome}"


class Diretorio(No):
    def __init__(self, nome: str) -> None:
        super().__init__(nome)
        self.filhos: list[No] = []

    def adicionar(self, *nos: No) -> "Diretorio":
        self.filhos.extend(nos)
        return self

    def tamanho(self) -> int:
        return sum(f.tamanho() for f in self.filhos)

    def listar(self, prefixo: str = "") -> Iterator[str]:
        caminho = f"{prefixo}{self.nome}/"
        yield caminho
        for f in self.filhos:
            yield from f.listar(caminho)
