"""Tabela de páginas de dois níveis com TLB (política LRU).

Endereço virtual de 32 bits: 10 bits de diretório | 10 bits de tabela | 12 bits de deslocamento
(páginas de 4 KiB). As tabelas de segundo nível só existem quando alguma página
sob elas é mapeada, o que economiza memória em espaços de endereços esparsos.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Optional

BITS_DIR = 10
BITS_TAB = 10
BITS_OFF = 12
TAMANHO_PAGINA = 1 << BITS_OFF


class FaltaDePagina(Exception):
    def __init__(self, endereco: int) -> None:
        super().__init__(f"falta de página em {endereco:#x}")
        self.endereco = endereco


def dividir(va: int) -> tuple[int, int, int]:
    """Retorna (índice_diretório, índice_tabela, deslocamento)."""
    if not 0 <= va < 1 << (BITS_DIR + BITS_TAB + BITS_OFF):
        raise ValueError("endereço virtual fora de 32 bits")
    off = va & (TAMANHO_PAGINA - 1)
    tab = (va >> BITS_OFF) & ((1 << BITS_TAB) - 1)
    dir_ = va >> (BITS_OFF + BITS_TAB)
    return dir_, tab, off


class TLB:
    def __init__(self, capacidade: int) -> None:
        if capacidade <= 0:
            raise ValueError("capacidade deve ser positiva")
        self.capacidade = capacidade
        self._entradas: OrderedDict[int, int] = OrderedDict()  # vpn -> quadro
        self.acertos = 0
        self.faltas = 0

    def buscar(self, vpn: int) -> Optional[int]:
        if vpn in self._entradas:
            self._entradas.move_to_end(vpn)
            self.acertos += 1
            return self._entradas[vpn]
        self.faltas += 1
        return None

    def inserir(self, vpn: int, quadro: int) -> None:
        self._entradas[vpn] = quadro
        self._entradas.move_to_end(vpn)
        if len(self._entradas) > self.capacidade:
            self._entradas.popitem(last=False)

    def invalidar(self, vpn: int) -> None:
        self._entradas.pop(vpn, None)

    @property
    def taxa_acerto(self) -> float:
        total = self.acertos + self.faltas
        return self.acertos / total if total else 0.0

    def vpns(self) -> list[int]:
        """VPNs em cache, do menos ao mais recentemente usado."""
        return list(self._entradas)


class MMU:
    def __init__(self, tlb_capacidade: int = 4) -> None:
        self.diretorio: dict[int, dict[int, int]] = {}
        self.tlb = TLB(tlb_capacidade)
        self.acessos_tabela = 0  # leituras de tabelas na memória (page walks)

    def mapear(self, vpn: int, quadro: int) -> None:
        dir_, tab = vpn >> BITS_TAB, vpn & ((1 << BITS_TAB) - 1)
        self.diretorio.setdefault(dir_, {})[tab] = quadro
        self.tlb.invalidar(vpn)

    def desmapear(self, vpn: int) -> None:
        dir_, tab = vpn >> BITS_TAB, vpn & ((1 << BITS_TAB) - 1)
        tabela = self.diretorio.get(dir_)
        if tabela is None or tab not in tabela:
            raise KeyError(vpn)
        del tabela[tab]
        if not tabela:
            del self.diretorio[dir_]  # libera a tabela de segundo nível vazia
        self.tlb.invalidar(vpn)

    @property
    def tabelas_alocadas(self) -> int:
        """Diretório raiz + tabelas de segundo nível existentes."""
        return 1 + len(self.diretorio)

    def traduzir(self, va: int) -> int:
        dir_, tab, off = dividir(va)
        vpn = va >> BITS_OFF
        quadro = self.tlb.buscar(vpn)
        if quadro is None:
            self.acessos_tabela += 1  # lê o diretório
            tabela = self.diretorio.get(dir_)
            if tabela is None:
                raise FaltaDePagina(va)
            self.acessos_tabela += 1  # lê a tabela de páginas
            if tab not in tabela:
                raise FaltaDePagina(va)
            quadro = tabela[tab]
            self.tlb.inserir(vpn, quadro)
        return quadro * TAMANHO_PAGINA + off


def tempo_efetivo_acesso(taxa_acerto: float, t_tlb: float, t_mem: float, niveis: int = 2) -> float:
    """TEA = h*(t_tlb + t_mem) + (1-h)*(t_tlb + (niveis+1)*t_mem)."""
    if not 0.0 <= taxa_acerto <= 1.0:
        raise ValueError("taxa de acerto fora de [0, 1]")
    acerto = t_tlb + t_mem
    erro = t_tlb + (niveis + 1) * t_mem
    return taxa_acerto * acerto + (1 - taxa_acerto) * erro
