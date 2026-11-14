"""k-d tree estática com vizinho mais próximo, k vizinhos e busca em raio."""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

Ponto = tuple[float, ...]


@dataclass
class _No:
    ponto: Ponto
    eixo: int
    esq: _No | None = None
    dir: _No | None = None


class KDTree:
    def __init__(self, pontos: list[Ponto]) -> None:
        if pontos:
            k = len(pontos[0])
            if k == 0 or any(len(p) != k for p in pontos):
                raise ValueError("pontos devem ter a mesma dimensão (>= 1)")
            self.dim = k
        else:
            self.dim = 0
        self._n = len(pontos)
        self._raiz = self._construir(list(pontos), 0)

    def __len__(self) -> int:
        return self._n

    def _construir(self, pts: list[Ponto], prof: int) -> _No | None:
        if not pts:
            return None
        eixo = prof % self.dim
        pts.sort(key=lambda p: p[eixo])
        m = len(pts) // 2
        return _No(pts[m], eixo, self._construir(pts[:m], prof + 1), self._construir(pts[m + 1 :], prof + 1))

    def mais_proximo(self, alvo: Ponto) -> Ponto | None:
        r = self.k_mais_proximos(alvo, 1)
        return r[0] if r else None

    def k_mais_proximos(self, alvo: Ponto, k: int) -> list[Ponto]:
        """Até k pontos mais próximos, do mais perto ao mais longe."""
        if k < 1:
            raise ValueError("k deve ser >= 1")
        if self._raiz is None:
            return []
        if len(alvo) != self.dim:
            raise ValueError("dimensão do alvo difere da árvore")
        heap: list[tuple[float, int, Ponto]] = []  # max-heap via distância negativa
        contador = [0]

        def visitar(no: _No | None) -> None:
            if no is None:
                return
            d2 = sum((a - b) ** 2 for a, b in zip(no.ponto, alvo))
            contador[0] += 1
            item = (-d2, contador[0], no.ponto)
            if len(heap) < k:
                heapq.heappush(heap, item)
            elif d2 < -heap[0][0]:
                heapq.heapreplace(heap, item)
            delta = alvo[no.eixo] - no.ponto[no.eixo]
            perto, longe = (no.esq, no.dir) if delta < 0 else (no.dir, no.esq)
            visitar(perto)
            if len(heap) < k or delta * delta < -heap[0][0]:
                visitar(longe)

        visitar(self._raiz)
        return [p for _, _, p in sorted(heap, key=lambda t: (-t[0], t[1]))]

    def no_raio(self, centro: Ponto, raio: float) -> list[Ponto]:
        """Pontos a distância <= raio do centro."""
        achados: list[Ponto] = []

        def visitar(no: _No | None) -> None:
            if no is None:
                return
            if math.dist(no.ponto, centro) <= raio:
                achados.append(no.ponto)
            delta = centro[no.eixo] - no.ponto[no.eixo]
            if delta - raio <= 0:
                visitar(no.esq)
            if delta + raio >= 0:
                visitar(no.dir)

        visitar(self._raiz)
        return achados
