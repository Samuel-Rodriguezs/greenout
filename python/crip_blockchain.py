"""Blockchain simples com proof of work (dificuldade em zeros hexadecimais iniciais).

AVISO: didático; sem rede, consenso ou assinaturas. Mantenha a dificuldade baixa.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass
class Bloco:
    indice: int
    dados: str
    anterior: str
    nonce: int = 0
    hash: str = ""

    def calcular_hash(self) -> str:
        corpo = json.dumps([self.indice, self.dados, self.anterior, self.nonce], ensure_ascii=False)
        return hashlib.sha256(corpo.encode()).hexdigest()

    def minerar(self, dificuldade: int) -> None:
        alvo = "0" * dificuldade
        self.nonce = 0
        self.hash = self.calcular_hash()
        while not self.hash.startswith(alvo):
            self.nonce += 1
            self.hash = self.calcular_hash()


class Blockchain:
    def __init__(self, dificuldade: int = 2) -> None:
        if dificuldade < 0:
            raise ValueError("dificuldade negativa")
        self.dificuldade = dificuldade
        genesis = Bloco(0, "genesis", "0" * 64)
        genesis.minerar(dificuldade)
        self.blocos: list[Bloco] = [genesis]

    def adicionar(self, dados: str) -> Bloco:
        b = Bloco(len(self.blocos), dados, self.blocos[-1].hash)
        b.minerar(self.dificuldade)
        self.blocos.append(b)
        return b

    def valida(self) -> bool:
        alvo = "0" * self.dificuldade
        for i, b in enumerate(self.blocos):
            if b.hash != b.calcular_hash() or not b.hash.startswith(alvo):
                return False
            if i == 0:
                if b.anterior != "0" * 64:
                    return False
            elif b.anterior != self.blocos[i - 1].hash or b.indice != i:
                return False
        return True
