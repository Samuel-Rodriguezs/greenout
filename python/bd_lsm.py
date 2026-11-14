"""LSM-tree simplificada: memtable + SSTables imutáveis em memória + compactação."""
from __future__ import annotations

from bisect import bisect_left
from typing import Any, Iterator, Optional

from bd_bloom import BloomFilter

LAPIDE = object()


class SSTable:
    def __init__(self, itens: list[tuple[Any, Any]], taxa_fp: float = 0.01) -> None:
        """`itens` já ordenados por chave e sem duplicatas."""
        self.chaves = [k for k, _ in itens]
        self.valores = [v for _, v in itens]
        self.bloom = BloomFilter.para(max(1, len(itens)), taxa_fp)
        for k in self.chaves:
            self.bloom.adicionar(k)
        self.consultas_ao_indice = 0

    def __len__(self) -> int:
        return len(self.chaves)

    def obter(self, chave: Any) -> tuple[bool, Any]:
        if chave not in self.bloom:
            return False, None
        self.consultas_ao_indice += 1
        i = bisect_left(self.chaves, chave)
        if i < len(self.chaves) and self.chaves[i] == chave:
            return True, self.valores[i]
        return False, None

    def itens(self) -> Iterator[tuple[Any, Any]]:
        return zip(self.chaves, self.valores)


class LSM:
    def __init__(self, limite_memtable: int = 4, max_tabelas: int = 4) -> None:
        if limite_memtable < 1 or max_tabelas < 2:
            raise ValueError("limite_memtable >= 1 e max_tabelas >= 2")
        self.limite = limite_memtable
        self.max_tabelas = max_tabelas
        self.memtable: dict[Any, Any] = {}
        self.tabelas: list[SSTable] = []  # da mais antiga para a mais nova
        self.compactacoes = 0

    def colocar(self, chave: Any, valor: Any) -> None:
        self.memtable[chave] = valor
        self._talvez_descarregar()

    def apagar(self, chave: Any) -> None:
        self.memtable[chave] = LAPIDE
        self._talvez_descarregar()

    def _talvez_descarregar(self) -> None:
        if len(self.memtable) >= self.limite:
            self.descarregar()

    def descarregar(self) -> None:
        if not self.memtable:
            return
        self.tabelas.append(SSTable(sorted(self.memtable.items(), key=lambda kv: kv[0])))
        self.memtable = {}
        if len(self.tabelas) > self.max_tabelas:
            self.compactar()

    def obter(self, chave: Any, padrao: Any = None) -> Any:
        if chave in self.memtable:
            v = self.memtable[chave]
            return padrao if v is LAPIDE else v
        for t in reversed(self.tabelas):
            achou, v = t.obter(chave)
            if achou:
                return padrao if v is LAPIDE else v
        return padrao

    def compactar(self) -> None:
        """Mescla todas as SSTables em uma (a mais nova vence); remove lápides."""
        if len(self.tabelas) < 2:
            return
        fundido: dict[Any, Any] = {}
        for t in self.tabelas:  # antigas primeiro: as novas sobrescrevem
            fundido.update(t.itens())
        vivos = sorted(((k, v) for k, v in fundido.items() if v is not LAPIDE), key=lambda kv: kv[0])
        self.tabelas = [SSTable(vivos)] if vivos else []
        self.compactacoes += 1

    def varrer(self, lo: Any = None, hi: Any = None) -> Iterator[tuple[Any, Any]]:
        """Itera chaves visíveis em ordem, lo <= k < hi."""
        visao: dict[Any, Any] = {}
        for t in self.tabelas:
            visao.update(t.itens())
        visao.update(self.memtable)
        for k in sorted(visao):
            if (lo is not None and k < lo) or (hi is not None and k >= hi):
                continue
            if visao[k] is not LAPIDE:
                yield k, visao[k]

    def __len__(self) -> int:
        return sum(1 for _ in self.varrer())
