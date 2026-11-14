"""Página de registros de tamanho variável (slotted page) com serialização struct.

Layout: [n_slots:H][fim_livre:H][slot0:(off:H,len:H)]...  ...[registros]
O diretório de slots cresce para a frente; os registros crescem do fim para trás.
Slot removido tem offset 0 (lápide); o número do slot é estável (compõe o RID).
"""
from __future__ import annotations

import struct
from typing import Iterator, Optional

CABECALHO = struct.Struct("<HH")
SLOT = struct.Struct("<HH")


class PaginaCheia(Exception):
    pass


class PaginaSlotted:
    def __init__(self, tamanho: int = 4096) -> None:
        if not CABECALHO.size + SLOT.size < tamanho <= 65535:
            raise ValueError("tamanho de página inválido")
        self.dados = bytearray(tamanho)
        CABECALHO.pack_into(self.dados, 0, 0, tamanho)

    @classmethod
    def de_bytes(cls, bruto: bytes) -> "PaginaSlotted":
        p = cls(len(bruto))
        p.dados = bytearray(bruto)
        n, fim = CABECALHO.unpack_from(p.dados, 0)
        if CABECALHO.size + n * SLOT.size > fim or fim > len(bruto):
            raise ValueError("página corrompida")
        return p

    def para_bytes(self) -> bytes:
        return bytes(self.dados)

    @property
    def n_slots(self) -> int:
        return CABECALHO.unpack_from(self.dados, 0)[0]

    @property
    def _fim_livre(self) -> int:
        return CABECALHO.unpack_from(self.dados, 0)[1]

    def espaco_livre(self) -> int:
        return self._fim_livre - CABECALHO.size - self.n_slots * SLOT.size

    def bytes_mortos(self) -> int:
        """Bytes ocupados por registros removidos/encolhidos (recuperáveis ao compactar)."""
        usados = sum(len(r) for _, r in self.registros())
        return len(self.dados) - self._fim_livre - usados

    def _slot(self, i: int) -> tuple[int, int]:
        if not 0 <= i < self.n_slots:
            raise IndexError(f"slot {i} inexistente")
        return SLOT.unpack_from(self.dados, CABECALHO.size + i * SLOT.size)

    def _gravar_slot(self, i: int, off: int, tam: int) -> None:
        SLOT.pack_into(self.dados, CABECALHO.size + i * SLOT.size, off, tam)

    def _slot_livre(self) -> Optional[int]:
        for i in range(self.n_slots):
            if self._slot(i)[0] == 0:
                return i
        return None

    def inserir(self, registro: bytes) -> int:
        if not registro:
            raise ValueError("registro vazio não é permitido")
        reutiliza = self._slot_livre()
        extra = 0 if reutiliza is not None else SLOT.size
        if len(registro) + extra > self.espaco_livre():
            self.compactar()
            if len(registro) + extra > self.espaco_livre():
                raise PaginaCheia()
        n, fim = CABECALHO.unpack_from(self.dados, 0)
        fim -= len(registro)
        self.dados[fim:fim + len(registro)] = registro
        i = reutiliza if reutiliza is not None else n
        if reutiliza is None:
            n += 1
        CABECALHO.pack_into(self.dados, 0, n, fim)
        self._gravar_slot(i, fim, len(registro))
        return i

    def ler(self, i: int) -> bytes:
        off, tam = self._slot(i)
        if off == 0:
            raise KeyError(f"slot {i} removido")
        return bytes(self.dados[off:off + tam])

    def remover(self, i: int) -> None:
        off, _ = self._slot(i)
        if off == 0:
            raise KeyError(f"slot {i} removido")
        self._gravar_slot(i, 0, 0)

    def atualizar(self, i: int, registro: bytes) -> None:
        off, tam = self._slot(i)
        if off == 0:
            raise KeyError(f"slot {i} removido")
        if not registro:
            raise ValueError("registro vazio não é permitido")
        if len(registro) <= tam:
            self.dados[off:off + len(registro)] = registro
            self._gravar_slot(i, off, len(registro))
            return
        antigo = bytes(self.dados[off:off + tam])
        self._gravar_slot(i, 0, 0)
        try:
            self.compactar()
            if len(registro) > self.espaco_livre():
                raise PaginaCheia()
            n, fim = CABECALHO.unpack_from(self.dados, 0)
            fim -= len(registro)
            self.dados[fim:fim + len(registro)] = registro
            CABECALHO.pack_into(self.dados, 0, n, fim)
            self._gravar_slot(i, fim, len(registro))
        except PaginaCheia:
            # restaura o registro antigo (a compactação liberou espaço suficiente para ele)
            n, fim = CABECALHO.unpack_from(self.dados, 0)
            fim -= len(antigo)
            self.dados[fim:fim + len(antigo)] = antigo
            CABECALHO.pack_into(self.dados, 0, n, fim)
            self._gravar_slot(i, fim, len(antigo))
            raise

    def compactar(self) -> None:
        """Reempacota os registros vivos no fim da página, preservando os slots."""
        vivos = [(i, self.ler(i)) for i in range(self.n_slots) if self._slot(i)[0] != 0]
        n = self.n_slots
        fim = len(self.dados)
        for i, reg in vivos:
            fim -= len(reg)
            self.dados[fim:fim + len(reg)] = reg
            self._gravar_slot(i, fim, len(reg))
        CABECALHO.pack_into(self.dados, 0, n, fim)

    def registros(self) -> Iterator[tuple[int, bytes]]:
        for i in range(self.n_slots):
            if self._slot(i)[0] != 0:
                yield i, self.ler(i)
