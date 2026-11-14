"""Numeração sequencial de peças processuais, por tipo e ano (ex.: PET-2024/0001)."""
from __future__ import annotations

import re

_PADRAO = re.compile(r"^([A-Z]{2,5})-(\d{4})/(\d{4,})$")

TIPOS = {"PET": "petição", "CON": "contestação", "REC": "recurso", "PAR": "parecer", "OFI": "ofício"}


class Numerador:
    def __init__(self, tipos: dict[str, str] | None = None) -> None:
        self.tipos = dict(tipos or TIPOS)
        self._ultimo: dict[tuple[str, int], int] = {}

    def proximo(self, tipo: str, ano: int) -> str:
        if tipo not in self.tipos:
            raise ValueError(f"tipo de peça desconhecido: {tipo}")
        if not 1900 <= ano <= 9999:
            raise ValueError("ano inválido")
        n = self._ultimo.get((tipo, ano), 0) + 1
        self._ultimo[(tipo, ano)] = n
        return f"{tipo}-{ano}/{n:04d}"

    def registrar_existente(self, numero: str) -> None:
        """Sincroniza o contador com um número já usado (ex.: importação de legado)."""
        tipo, ano, seq = interpretar(numero)
        if tipo not in self.tipos:
            raise ValueError(f"tipo de peça desconhecido: {tipo}")
        chave = (tipo, ano)
        self._ultimo[chave] = max(self._ultimo.get(chave, 0), seq)

    def ultimo(self, tipo: str, ano: int) -> int:
        return self._ultimo.get((tipo, ano), 0)

    def lacunas(self, tipo: str, ano: int, usados: list[int]) -> list[int]:
        """Números faltando entre 1 e o maior já utilizado."""
        if not usados:
            return []
        s = set(usados)
        return [i for i in range(1, max(s) + 1) if i not in s]


def interpretar(numero: str) -> tuple[str, int, int]:
    m = _PADRAO.match(numero)
    if not m:
        raise ValueError(f"número de peça inválido: {numero}")
    return m.group(1), int(m.group(2)), int(m.group(3))
