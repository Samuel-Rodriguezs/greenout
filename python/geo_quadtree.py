"""Quadtree de pontos com busca em retângulo e vizinho mais próximo."""
from __future__ import annotations

import math

from geo_aabb import AABB

Ponto = tuple[float, float]


class Quadtree:
    def __init__(self, limites: AABB, capacidade: int = 4, profundidade_max: int = 16) -> None:
        if capacidade < 1:
            raise ValueError("capacidade deve ser >= 1")
        self.limites = limites
        self.capacidade = capacidade
        self._prof_max = profundidade_max
        self._pontos: list[Ponto] = []
        self._filhos: list[Quadtree] | None = None
        self._n = 0

    def __len__(self) -> int:
        return self._n

    def inserir(self, p: Ponto) -> bool:
        """Insere p; False se está fora dos limites."""
        if not self.limites.contem_ponto(p):
            return False
        self._n += 1
        self._inserir(p, 0)
        return True

    def _inserir(self, p: Ponto, prof: int) -> None:
        if self._filhos is None:
            if len(self._pontos) < self.capacidade or prof >= self._prof_max:
                self._pontos.append(p)
                return
            self._dividir(prof)
        self._filho_de(p)._contar_e_inserir(p, prof + 1)

    def _contar_e_inserir(self, p: Ponto, prof: int) -> None:
        self._n += 1
        self._inserir(p, prof)

    def _dividir(self, prof: int) -> None:
        b = self.limites
        cx, cy = b.centro
        self._filhos = [
            Quadtree(AABB(b.xmin, b.ymin, cx, cy), self.capacidade, self._prof_max),
            Quadtree(AABB(cx, b.ymin, b.xmax, cy), self.capacidade, self._prof_max),
            Quadtree(AABB(b.xmin, cy, cx, b.ymax), self.capacidade, self._prof_max),
            Quadtree(AABB(cx, cy, b.xmax, b.ymax), self.capacidade, self._prof_max),
        ]
        antigos, self._pontos = self._pontos, []
        for q in antigos:
            self._filho_de(q)._contar_e_inserir(q, prof + 1)

    def _filho_de(self, p: Ponto) -> Quadtree:
        assert self._filhos is not None
        cx, cy = self.limites.centro
        return self._filhos[(p[0] >= cx) + 2 * (p[1] >= cy)]

    def buscar(self, area: AABB) -> list[Ponto]:
        """Todos os pontos dentro da área (bordas inclusas)."""
        if not self.limites.intersecta(area):
            return []
        if self._filhos is None:
            return [p for p in self._pontos if area.contem_ponto(p)]
        achados: list[Ponto] = []
        for f in self._filhos:
            achados.extend(f.buscar(area))
        return achados

    def mais_proximo(self, alvo: Ponto) -> Ponto | None:
        melhor: list = [math.inf, None]
        self._vizinho(alvo, melhor)
        return melhor[1]

    def _vizinho(self, alvo: Ponto, melhor: list) -> None:
        if self._n == 0 or self.limites.distancia_ao_ponto(alvo) >= melhor[0]:
            return
        if self._filhos is None:
            for p in self._pontos:
                d = math.dist(p, alvo)
                if d < melhor[0]:
                    melhor[0], melhor[1] = d, p
            return
        for f in sorted(self._filhos, key=lambda f: f.limites.distancia_ao_ponto(alvo)):
            f._vizinho(alvo, melhor)
