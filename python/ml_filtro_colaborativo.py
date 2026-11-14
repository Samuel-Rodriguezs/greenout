"""Filtro colaborativo baseado em usuários (similaridade de cosseno)."""
from __future__ import annotations

import math

Avaliacoes = dict[str, dict[str, float]]


def similaridade_cosseno(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosseno sobre os itens avaliados por ambos (0 se não houver interseção)."""
    comuns = set(a) & set(b)
    if not comuns:
        return 0.0
    num = sum(a[i] * b[i] for i in comuns)
    den = math.sqrt(sum(a[i] ** 2 for i in comuns)) * math.sqrt(sum(b[i] ** 2 for i in comuns))
    return num / den if den else 0.0


def similaridade_pearson(a: dict[str, float], b: dict[str, float]) -> float:
    comuns = sorted(set(a) & set(b))
    if len(comuns) < 2:
        return 0.0
    ma = sum(a[i] for i in comuns) / len(comuns)
    mb = sum(b[i] for i in comuns) / len(comuns)
    num = sum((a[i] - ma) * (b[i] - mb) for i in comuns)
    den = math.sqrt(sum((a[i] - ma) ** 2 for i in comuns)) * math.sqrt(sum((b[i] - mb) ** 2 for i in comuns))
    return num / den if den else 0.0


class FiltroColaborativo:
    def __init__(self, avaliacoes: Avaliacoes, similaridade=similaridade_cosseno) -> None:
        self.avaliacoes = avaliacoes
        self.similaridade = similaridade

    def vizinhos(self, usuario: str, k: int = 3) -> list[tuple[str, float]]:
        if usuario not in self.avaliacoes:
            raise KeyError(f"usuário desconhecido: {usuario}")
        sims = [(u, self.similaridade(self.avaliacoes[usuario], r))
                for u, r in self.avaliacoes.items() if u != usuario]
        sims = [(u, s) for u, s in sims if s > 0]
        return sorted(sims, key=lambda p: (-p[1], p[0]))[:k]

    def prever(self, usuario: str, item: str, k: int = 3) -> float | None:
        """Média ponderada das notas dos k vizinhos mais similares que avaliaram o item."""
        viz = [(u, s) for u, s in self.vizinhos(usuario, k=len(self.avaliacoes))
               if item in self.avaliacoes[u]][:k]
        return self._prever_com_vizinhos(usuario, item, viz)

    def recomendar(self, usuario: str, n: int = 3, k: int = 3) -> list[tuple[str, float]]:
        vistos = set(self.avaliacoes[usuario])
        candidatos = {i for r in self.avaliacoes.values() for i in r} - vistos
        previsoes = []
        for item in candidatos:
            p = self._prever_com_vizinhos(usuario, item, self.vizinhos(usuario, k))
            if p is not None:
                previsoes.append((item, p))
        return sorted(previsoes, key=lambda p: (-p[1], p[0]))[:n]

    def _prever_com_vizinhos(self, usuario: str, item: str, viz: list[tuple[str, float]]) -> float | None:
        com_item = [(s, self.avaliacoes[u][item]) for u, s in viz if item in self.avaliacoes[u]]
        den = sum(s for s, _ in com_item)
        return sum(s * n for s, n in com_item) / den if den else None
