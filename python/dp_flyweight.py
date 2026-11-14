"""Flyweight: estilos de caractere compartilhados em um editor de texto."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Estilo:
    fonte: str
    tamanho: int
    negrito: bool = False


class FabricaEstilos:
    def __init__(self) -> None:
        self._cache: dict[tuple, Estilo] = {}

    def obter(self, fonte: str, tamanho: int, negrito: bool = False) -> Estilo:
        chave = (fonte, tamanho, negrito)
        if chave not in self._cache:
            self._cache[chave] = Estilo(fonte, tamanho, negrito)
        return self._cache[chave]

    def total(self) -> int:
        return len(self._cache)


class Documento:
    def __init__(self, fabrica: FabricaEstilos) -> None:
        self._fabrica = fabrica
        self._caracteres: list[tuple[str, Estilo]] = []

    def escrever(self, texto: str, fonte: str = "Arial", tamanho: int = 12,
                 negrito: bool = False) -> None:
        estilo = self._fabrica.obter(fonte, tamanho, negrito)
        self._caracteres.extend((c, estilo) for c in texto)

    def texto(self) -> str:
        return "".join(c for c, _ in self._caracteres)

    def estilo_em(self, pos: int) -> Estilo:
        return self._caracteres[pos][1]
