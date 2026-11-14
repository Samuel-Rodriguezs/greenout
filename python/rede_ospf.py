"""Estado de enlace no estilo OSPF: LSDB com números de sequência e SPF (Dijkstra)."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LSA:
    roteador: str
    seq: int
    enlaces: tuple[tuple[str, int], ...]  # (vizinho, custo)


@dataclass
class LSDB:
    lsas: dict[str, LSA] = field(default_factory=dict)

    def instalar(self, lsa: LSA) -> bool:
        """Aceita apenas LSAs mais novas (flooding); True se foi instalada."""
        atual = self.lsas.get(lsa.roteador)
        if atual is not None and atual.seq >= lsa.seq:
            return False
        for _, custo in lsa.enlaces:
            if custo <= 0:
                raise ValueError("custo de enlace deve ser positivo")
        self.lsas[lsa.roteador] = lsa
        return True

    def grafo(self) -> dict[str, dict[str, int]]:
        """Só considera enlaces bidirecionais (two-way check)."""
        g: dict[str, dict[str, int]] = {r: {} for r in self.lsas}
        for r, lsa in self.lsas.items():
            for viz, custo in lsa.enlaces:
                outro = self.lsas.get(viz)
                if outro and any(v == r for v, _ in outro.enlaces):
                    g[r][viz] = custo
        return g


def spf(lsdb: LSDB, origem: str) -> tuple[dict[str, int], dict[str, set[str]]]:
    """Dijkstra. Devolve (distâncias, predecessores) com todos os predecessores de empate."""
    g = lsdb.grafo()
    if origem not in g:
        raise KeyError(origem)
    dist = {origem: 0}
    pred: dict[str, set[str]] = {origem: set()}
    fila = [(0, origem)]
    visitado: set[str] = set()
    while fila:
        d, u = heapq.heappop(fila)
        if u in visitado:
            continue
        visitado.add(u)
        for v, c in g[u].items():
            nd = d + c
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                pred[v] = {u}
                heapq.heappush(fila, (nd, v))
            elif nd == dist[v]:
                pred[v].add(u)
    return dist, pred


def tabela_de_rotas(lsdb: LSDB, origem: str) -> dict[str, tuple[int, set[str]]]:
    """destino -> (custo, conjunto de primeiros saltos); mais de um = ECMP."""
    dist, pred = spf(lsdb, origem)
    saltos: dict[str, set[str]] = {origem: set()}

    def primeiros(no: str) -> set[str]:
        if no in saltos:
            return saltos[no]
        res: set[str] = set()
        for p in pred[no]:
            res |= {no} if p == origem else primeiros(p)
        saltos[no] = res
        return res

    return {d: (c, primeiros(d)) for d, c in dist.items() if d != origem}


def caminho(lsdb: LSDB, origem: str, destino: str) -> list[str] | None:
    """Um dos caminhos mais curtos (o lexicograficamente menor), ou None."""
    dist, pred = spf(lsdb, origem)
    if destino not in dist:
        return None
    rota = [destino]
    while rota[-1] != origem:
        rota.append(min(pred[rota[-1]]))
    return rota[::-1]


def lsdb_de_grafo(enlaces: list[tuple[str, str, int]]) -> LSDB:
    """Constrói uma LSDB simétrica a partir de enlaces (a, b, custo)."""
    adj: dict[str, list[tuple[str, int]]] = {}
    for a, b, c in enlaces:
        adj.setdefault(a, []).append((b, c))
        adj.setdefault(b, []).append((a, c))
    db = LSDB()
    for r, viz in adj.items():
        db.instalar(LSA(r, 1, tuple(sorted(viz))))
    return db
