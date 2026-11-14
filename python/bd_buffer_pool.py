"""Buffer pool com política de substituição LRU ou Clock (segunda chance).

O disco é abstraído por duas funções: `ler(id_pagina) -> bytes` e
`gravar(id_pagina, dados)`. Páginas com pin > 0 nunca são despejadas.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Callable, Optional


class BufferCheio(Exception):
    """Todas as molduras estão fixadas (pin) e não há como despejar."""


class Moldura:
    def __init__(self) -> None:
        self.id_pagina: Optional[int] = None
        self.dados: bytearray = bytearray()
        self.sujo = False
        self.pin = 0
        self.referencia = False


class BufferPool:
    def __init__(self, capacidade: int, ler: Callable[[int], bytes],
                 gravar: Callable[[int, bytes], None], politica: str = "lru") -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        if politica not in ("lru", "clock"):
            raise ValueError("política deve ser 'lru' ou 'clock'")
        self.capacidade = capacidade
        self.politica = politica
        self._ler, self._gravar = ler, gravar
        self.molduras = [Moldura() for _ in range(capacidade)]
        self.tabela: dict[int, int] = {}
        self._lru: "OrderedDict[int, None]" = OrderedDict()  # índices de moldura, mais antigo primeiro
        self._ponteiro = 0
        self.acertos = 0
        self.faltas = 0
        self.despejos = 0

    def _escolher_vitima(self) -> int:
        for i, m in enumerate(self.molduras):
            if m.id_pagina is None:
                return i
        if self.politica == "lru":
            for i in self._lru:
                if self.molduras[i].pin == 0:
                    return i
            raise BufferCheio()
        # clock: no máximo duas voltas completas
        for _ in range(2 * self.capacidade):
            m = self.molduras[self._ponteiro]
            i = self._ponteiro
            self._ponteiro = (self._ponteiro + 1) % self.capacidade
            if m.pin > 0:
                continue
            if m.referencia:
                m.referencia = False
                continue
            return i
        raise BufferCheio()

    def _tocar(self, i: int) -> None:
        self.molduras[i].referencia = True
        if i in self._lru:
            self._lru.move_to_end(i)
        else:
            self._lru[i] = None

    def buscar(self, id_pagina: int) -> bytearray:
        """Traz a página para o pool, fixa (pin) e devolve seus dados mutáveis."""
        i = self.tabela.get(id_pagina)
        if i is not None:
            self.acertos += 1
        else:
            self.faltas += 1
            i = self._escolher_vitima()
            m = self.molduras[i]
            novos = bytearray(self._ler(id_pagina))  # lê antes de despejar: falha não perde a vítima
            if m.id_pagina is not None:
                if m.sujo:
                    self._gravar(m.id_pagina, bytes(m.dados))
                del self.tabela[m.id_pagina]
                self._lru.pop(i, None)
                self.despejos += 1
            m.dados = novos
            m.id_pagina, m.sujo, m.pin = id_pagina, False, 0
            self.tabela[id_pagina] = i
        self.molduras[i].pin += 1
        self._tocar(i)
        return self.molduras[i].dados

    def liberar(self, id_pagina: int, sujo: bool = False) -> None:
        i = self.tabela.get(id_pagina)
        if i is None:
            raise KeyError(f"página {id_pagina} não está no pool")
        m = self.molduras[i]
        if m.pin == 0:
            raise ValueError(f"página {id_pagina} não está fixada")
        m.pin -= 1
        m.sujo = m.sujo or sujo

    def descarregar(self, id_pagina: Optional[int] = None) -> None:
        """Grava páginas sujas (uma ou todas) sem despejá-las."""
        alvos = [self.tabela[id_pagina]] if id_pagina is not None else list(self.tabela.values())
        for i in alvos:
            m = self.molduras[i]
            if m.sujo and m.id_pagina is not None:
                self._gravar(m.id_pagina, bytes(m.dados))
                m.sujo = False

    def residentes(self) -> list[int]:
        return sorted(self.tabela)
