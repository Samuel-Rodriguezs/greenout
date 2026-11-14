"""Máquina de estados do ciclo de vida do processo, com histórico de transições."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class Estado(Enum):
    CADASTRADO = "cadastrado"
    EM_ANDAMENTO = "em_andamento"
    SUSPENSO = "suspenso"
    SENTENCIADO = "sentenciado"
    EM_RECURSO = "em_recurso"
    TRANSITADO = "transitado"
    EM_EXECUCAO = "em_execucao"
    ARQUIVADO = "arquivado"


TRANSICOES: dict[Estado, frozenset[Estado]] = {
    Estado.CADASTRADO: frozenset({Estado.EM_ANDAMENTO, Estado.ARQUIVADO}),
    Estado.EM_ANDAMENTO: frozenset({Estado.SUSPENSO, Estado.SENTENCIADO, Estado.ARQUIVADO}),
    Estado.SUSPENSO: frozenset({Estado.EM_ANDAMENTO, Estado.ARQUIVADO}),
    Estado.SENTENCIADO: frozenset({Estado.EM_RECURSO, Estado.TRANSITADO}),
    Estado.EM_RECURSO: frozenset({Estado.SENTENCIADO, Estado.TRANSITADO}),
    Estado.TRANSITADO: frozenset({Estado.EM_EXECUCAO, Estado.ARQUIVADO}),
    Estado.EM_EXECUCAO: frozenset({Estado.ARQUIVADO}),
    Estado.ARQUIVADO: frozenset({Estado.EM_ANDAMENTO}),  # desarquivamento
}


class TransicaoInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Transicao:
    origem: Estado
    destino: Estado
    data: date
    motivo: str = ""


class CicloProcesso:
    def __init__(self, inicial: Estado = Estado.CADASTRADO) -> None:
        self.estado = inicial
        self.historico: list[Transicao] = []

    def pode(self, destino: Estado) -> bool:
        return destino in TRANSICOES[self.estado]

    def destinos(self) -> list[Estado]:
        return sorted(TRANSICOES[self.estado], key=lambda e: e.value)

    def transitar(self, destino: Estado, data: date, motivo: str = "") -> Transicao:
        if not self.pode(destino):
            raise TransicaoInvalida(f"{self.estado.value} -> {destino.value} não permitido")
        if destino == Estado.SUSPENSO and not motivo.strip():
            raise ValueError("suspensão exige motivo")
        if self.historico and data < self.historico[-1].data:
            raise ValueError("data anterior à última transição")
        t = Transicao(self.estado, destino, data, motivo.strip())
        self.historico.append(t)
        self.estado = destino
        return t

    @property
    def finalizado(self) -> bool:
        return self.estado == Estado.ARQUIVADO

    def tempo_em(self, estado: Estado, hoje: date) -> int:
        """Dias totais passados no estado informado (inclui o período corrente)."""
        total = 0
        for i, t in enumerate(self.historico):
            if t.origem == estado:
                inicio = self.historico[i - 1].data if i else None
                if inicio is not None:
                    total += (t.data - inicio).days
        if self.historico and self.estado == estado:
            total += (hoje - self.historico[-1].data).days
        return total

    def alcancaveis(self) -> set[Estado]:
        """Todos os estados atingíveis a partir do atual (busca em largura)."""
        vistos: set[Estado] = set()
        fila = [self.estado]
        while fila:
            for d in TRANSICOES[fila.pop(0)]:
                if d not in vistos:
                    vistos.add(d)
                    fila.append(d)
        return vistos
