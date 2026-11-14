"""Índice hash extensível: diretório de 2**profundidade_global ponteiros para baldes."""
from __future__ import annotations

import zlib
from typing import Any, Optional


def hash_chave(chave: Any) -> int:
    """Hash determinístico de 32 bits (independe de PYTHONHASHSEED)."""
    return zlib.crc32(repr(chave).encode("utf-8"))


class Balde:
    def __init__(self, profundidade: int, capacidade: int) -> None:
        self.profundidade = profundidade
        self.capacidade = capacidade
        self.itens: dict[Any, Any] = {}


class HashExtensivel:
    MAX_PROFUNDIDADE = 24

    def __init__(self, capacidade_balde: int = 4) -> None:
        if capacidade_balde < 1:
            raise ValueError("capacidade deve ser >= 1")
        self.capacidade = capacidade_balde
        self.profundidade = 0
        self.diretorio: list[Balde] = [Balde(0, capacidade_balde)]
        self.tamanho = 0

    def __len__(self) -> int:
        return self.tamanho

    def _indice(self, chave: Any) -> int:
        return hash_chave(chave) & ((1 << self.profundidade) - 1)

    def buscar(self, chave: Any, padrao: Optional[Any] = None) -> Any:
        return self.diretorio[self._indice(chave)].itens.get(chave, padrao)

    def __contains__(self, chave: Any) -> bool:
        return chave in self.diretorio[self._indice(chave)].itens

    def inserir(self, chave: Any, valor: Any = None) -> None:
        balde = self.diretorio[self._indice(chave)]
        if chave in balde.itens:
            balde.itens[chave] = valor
            return
        while len(balde.itens) >= balde.capacidade:
            if not self._dividir(balde):
                # todas as chaves colidem em todos os bits permitidos: balde de estouro
                break
            balde = self.diretorio[self._indice(chave)]
        balde.itens[chave] = valor
        self.tamanho += 1

    def _dividir(self, balde: Balde) -> bool:
        if balde.profundidade == self.profundidade:
            if self.profundidade >= self.MAX_PROFUNDIDADE:
                return False
            self.diretorio = self.diretorio + self.diretorio
            self.profundidade += 1
        nova_prof = balde.profundidade + 1
        a = Balde(nova_prof, self.capacidade)
        b = Balde(nova_prof, self.capacidade)
        bit = 1 << balde.profundidade
        for k, v in balde.itens.items():
            (b if hash_chave(k) & bit else a).itens[k] = v
        for i in range(len(self.diretorio)):
            if self.diretorio[i] is balde:
                self.diretorio[i] = b if i & bit else a
        return True

    def remover(self, chave: Any) -> bool:
        balde = self.diretorio[self._indice(chave)]
        if chave not in balde.itens:
            return False
        del balde.itens[chave]
        self.tamanho -= 1
        self._tentar_fundir(balde)
        return True

    def _tentar_fundir(self, balde: Balde) -> None:
        while balde.profundidade > 0:
            bit = 1 << (balde.profundidade - 1)
            idx = next(i for i, b in enumerate(self.diretorio) if b is balde)
            irmao = self.diretorio[idx ^ bit]
            if irmao is balde or irmao.profundidade != balde.profundidade:
                break
            if len(irmao.itens) + len(balde.itens) > self.capacidade:
                break
            fundido = Balde(balde.profundidade - 1, self.capacidade)
            fundido.itens = {**irmao.itens, **balde.itens}
            for i in range(len(self.diretorio)):
                if self.diretorio[i] is balde or self.diretorio[i] is irmao:
                    self.diretorio[i] = fundido
            balde = fundido
        self._encolher()

    def _encolher(self) -> None:
        while self.profundidade > 0 and all(b.profundidade < self.profundidade for b in self.diretorio):
            self.diretorio = self.diretorio[: len(self.diretorio) // 2]
            self.profundidade -= 1

    def baldes_distintos(self) -> int:
        return len({id(b) for b in self.diretorio})

    def chaves(self) -> list[Any]:
        vistos: set[int] = set()
        saida: list[Any] = []
        for b in self.diretorio:
            if id(b) not in vistos:
                vistos.add(id(b))
                saida.extend(b.itens)
        return saida
