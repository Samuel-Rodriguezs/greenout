"""Heap file em disco: páginas slotted de tamanho fixo, endereçadas por RID (página, slot)."""
from __future__ import annotations

import os
from typing import Iterator, NamedTuple

from bd_pagina_slotted import PaginaCheia, PaginaSlotted


class RID(NamedTuple):
    pagina: int
    slot: int


class HeapFile:
    def __init__(self, caminho: str, tamanho_pagina: int = 512) -> None:
        self.caminho = caminho
        self.tamanho_pagina = tamanho_pagina
        modo = "r+b" if os.path.exists(caminho) else "w+b"
        self._f = open(caminho, modo)
        self._f.seek(0, os.SEEK_END)
        total = self._f.tell()
        if total % tamanho_pagina:
            self._f.close()
            raise ValueError("arquivo com tamanho incompatível com o tamanho de página")
        self.n_paginas = total // tamanho_pagina
        self._livre = {i: self._recuperavel(self._ler_pagina(i)) for i in range(self.n_paginas)}

    @staticmethod
    def _recuperavel(p: PaginaSlotted) -> int:
        """Espaço disponível após compactar (inclui buracos de registros removidos)."""
        return p.espaco_livre() + p.bytes_mortos()

    def fechar(self) -> None:
        if not self._f.closed:
            self._f.flush()
            self._f.close()

    def __enter__(self) -> "HeapFile":
        return self

    def __exit__(self, *exc) -> None:
        self.fechar()

    def _ler_pagina(self, n: int) -> PaginaSlotted:
        if not 0 <= n < self.n_paginas:
            raise IndexError(f"página {n} inexistente")
        self._f.seek(n * self.tamanho_pagina)
        return PaginaSlotted.de_bytes(self._f.read(self.tamanho_pagina))

    def _gravar_pagina(self, n: int, p: PaginaSlotted) -> None:
        self._f.seek(n * self.tamanho_pagina)
        self._f.write(p.para_bytes())
        self._livre[n] = self._recuperavel(p)

    def inserir(self, registro: bytes) -> RID:
        # +4: pior caso precisa de um novo slot
        for n, livre in self._livre.items():
            if livre >= len(registro) + 4:
                p = self._ler_pagina(n)
                try:
                    s = p.inserir(registro)
                except PaginaCheia:
                    continue
                self._gravar_pagina(n, p)
                return RID(n, s)
        p = PaginaSlotted(self.tamanho_pagina)
        try:
            s = p.inserir(registro)
        except PaginaCheia:
            raise ValueError("registro maior que a capacidade de uma página") from None
        n = self.n_paginas
        self.n_paginas += 1
        self._gravar_pagina(n, p)
        return RID(n, s)

    def ler(self, rid: RID) -> bytes:
        return self._ler_pagina(rid.pagina).ler(rid.slot)

    def remover(self, rid: RID) -> None:
        p = self._ler_pagina(rid.pagina)
        p.remover(rid.slot)
        self._gravar_pagina(rid.pagina, p)

    def atualizar(self, rid: RID, registro: bytes) -> RID:
        """Atualiza in-place se couber; senão move o registro e devolve o novo RID."""
        p = self._ler_pagina(rid.pagina)
        try:
            p.atualizar(rid.slot, registro)
        except PaginaCheia:
            p.ler(rid.slot)  # garante que o RID é válido antes de mover
            novo = self.inserir(registro)
            self.remover(rid)
            return novo
        self._gravar_pagina(rid.pagina, p)
        return rid

    def varrer(self) -> Iterator[tuple[RID, bytes]]:
        for n in range(self.n_paginas):
            for s, reg in self._ler_pagina(n).registros():
                yield RID(n, s), reg
