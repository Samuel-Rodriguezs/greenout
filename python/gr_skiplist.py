"""Skip list: conjunto ordenado probabilístico."""

from __future__ import annotations

import random
from typing import Iterator, Optional


class _No:
    def __init__(self, chave: Optional[int], nivel: int) -> None:
        self.chave = chave
        self.prox: list[Optional[_No]] = [None] * nivel


class SkipList:
    def __init__(self, nivel_max: int = 16, p: float = 0.5, semente: Optional[int] = None) -> None:
        if nivel_max < 1 or not 0 < p < 1:
            raise ValueError("parâmetros inválidos")
        self._max = nivel_max
        self._p = p
        self._rnd = random.Random(semente)
        self._cabeca = _No(None, nivel_max)
        self._nivel = 1
        self._tam = 0

    def __len__(self) -> int:
        return self._tam

    def _nivel_aleatorio(self) -> int:
        n = 1
        while n < self._max and self._rnd.random() < self._p:
            n += 1
        return n

    def _predecessores(self, chave: int) -> list[_No]:
        atualiza = [self._cabeca] * self._max
        no = self._cabeca
        for i in range(self._nivel - 1, -1, -1):
            while no.prox[i] is not None and no.prox[i].chave < chave:
                no = no.prox[i]
            atualiza[i] = no
        return atualiza

    def __contains__(self, chave: int) -> bool:
        cand = self._predecessores(chave)[0].prox[0]
        return cand is not None and cand.chave == chave

    def inserir(self, chave: int) -> bool:
        atualiza = self._predecessores(chave)
        cand = atualiza[0].prox[0]
        if cand is not None and cand.chave == chave:
            return False
        nivel = self._nivel_aleatorio()
        if nivel > self._nivel:
            self._nivel = nivel
        novo = _No(chave, nivel)
        for i in range(nivel):
            novo.prox[i] = atualiza[i].prox[i]
            atualiza[i].prox[i] = novo
        self._tam += 1
        return True

    def remover(self, chave: int) -> bool:
        atualiza = self._predecessores(chave)
        alvo = atualiza[0].prox[0]
        if alvo is None or alvo.chave != chave:
            return False
        for i in range(len(alvo.prox)):
            if atualiza[i].prox[i] is alvo:
                atualiza[i].prox[i] = alvo.prox[i]
        while self._nivel > 1 and self._cabeca.prox[self._nivel - 1] is None:
            self._nivel -= 1
        self._tam -= 1
        return True

    def __iter__(self) -> Iterator[int]:
        no = self._cabeca.prox[0]
        while no is not None:
            yield no.chave
            no = no.prox[0]

    def menor_maior_igual(self, chave: int) -> Optional[int]:
        """Menor elemento >= chave, ou None."""
        cand = self._predecessores(chave)[0].prox[0]
        return cand.chave if cand else None
