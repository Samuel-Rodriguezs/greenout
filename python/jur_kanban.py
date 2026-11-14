"""Kanban de status de processos, com colunas ordenadas e limite de itens em andamento (WIP)."""
from __future__ import annotations

COLUNAS_PADRAO = ["triagem", "peticionar", "aguardando", "audiencia", "recurso", "encerrado"]


class Kanban:
    def __init__(self, colunas: list[str] | None = None, limites: dict[str, int] | None = None) -> None:
        cols = list(colunas or COLUNAS_PADRAO)
        if len(set(cols)) != len(cols) or not cols:
            raise ValueError("colunas devem ser únicas e não vazias")
        self.colunas = cols
        self.limites = dict(limites or {})
        for c in self.limites:
            if c not in cols:
                raise ValueError(f"limite para coluna inexistente: {c}")
        self._local: dict[str, str] = {}
        self._cartoes: dict[str, list[str]] = {c: [] for c in cols}

    def adicionar(self, processo: str, coluna: str | None = None) -> None:
        coluna = coluna or self.colunas[0]
        if processo in self._local:
            raise ValueError(f"processo {processo} já está no quadro")
        self._checar(coluna)
        self._cartoes[coluna].append(processo)
        self._local[processo] = coluna

    def _checar(self, coluna: str) -> None:
        if coluna not in self._cartoes:
            raise KeyError(f"coluna inexistente: {coluna}")
        lim = self.limites.get(coluna)
        if lim is not None and len(self._cartoes[coluna]) >= lim:
            raise ValueError(f"limite de {lim} itens atingido em '{coluna}'")

    def mover(self, processo: str, destino: str) -> None:
        origem = self.coluna_de(processo)
        if origem == destino:
            return
        self._checar(destino)
        self._cartoes[origem].remove(processo)
        self._cartoes[destino].append(processo)
        self._local[processo] = destino

    def avancar(self, processo: str) -> str:
        i = self.colunas.index(self.coluna_de(processo))
        if i == len(self.colunas) - 1:
            raise ValueError("processo já está na última coluna")
        self.mover(processo, self.colunas[i + 1])
        return self.colunas[i + 1]

    def coluna_de(self, processo: str) -> str:
        if processo not in self._local:
            raise KeyError(f"processo {processo} não está no quadro")
        return self._local[processo]

    def remover(self, processo: str) -> None:
        self._cartoes[self.coluna_de(processo)].remove(processo)
        del self._local[processo]

    def quadro(self) -> dict[str, list[str]]:
        return {c: list(v) for c, v in self._cartoes.items()}

    def contagem(self) -> dict[str, int]:
        return {c: len(v) for c, v in self._cartoes.items()}
