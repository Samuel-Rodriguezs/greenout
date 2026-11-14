"""Árvore de Merkle com prova de inclusão (SHA-256, prefixos de domínio).

AVISO: didático. Folhas usam prefixo 0x00 e nós internos 0x01 (evita ataque de segunda pré-imagem).
Nível ímpar: o último nó é promovido sem duplicação.
"""
from __future__ import annotations

import hashlib


def _folha(dado: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + dado).digest()


def _no(esq: bytes, dir_: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + esq + dir_).digest()


class ArvoreMerkle:
    def __init__(self, dados: list[bytes]) -> None:
        if not dados:
            raise ValueError("sem dados")
        self.niveis: list[list[bytes]] = [[_folha(d) for d in dados]]
        while len(self.niveis[-1]) > 1:
            atual = self.niveis[-1]
            prox = [_no(atual[i], atual[i + 1]) for i in range(0, len(atual) - 1, 2)]
            if len(atual) % 2:
                prox.append(atual[-1])
            self.niveis.append(prox)

    @property
    def raiz(self) -> bytes:
        return self.niveis[-1][0]

    def prova(self, indice: int) -> list[tuple[str, bytes]]:
        """Lista de (lado_do_irmao, hash) da folha até a raiz."""
        if not 0 <= indice < len(self.niveis[0]):
            raise IndexError("índice fora do intervalo")
        caminho = []
        for nivel in self.niveis[:-1]:
            irmao = indice ^ 1
            if irmao < len(nivel):
                caminho.append(("D" if irmao > indice else "E", nivel[irmao]))
            indice //= 2
        return caminho


def verificar_prova(dado: bytes, prova: list[tuple[str, bytes]], raiz: bytes) -> bool:
    h = _folha(dado)
    for lado, irmao in prova:
        h = _no(h, irmao) if lado == "D" else _no(irmao, h)
    return h == raiz
