"""Ordenação topológica (Kahn) determinística, com detecção de ciclos."""
import heapq
from typing import Dict, Hashable, Iterable, List, Set


class CicloDetectado(ValueError):
    pass


def ordenar_topologicamente(dependencias: Dict[Hashable, Iterable[Hashable]]) -> List[Hashable]:
    """dependencias[x] = itens que devem vir ANTES de x. Empates resolvidos pela ordem natural."""
    pais: Dict[Hashable, Set[Hashable]] = {}
    filhos: Dict[Hashable, Set[Hashable]] = {}
    for no, deps in dependencias.items():
        pais.setdefault(no, set())
        filhos.setdefault(no, set())
        for d in deps:
            pais[no].add(d)
            pais.setdefault(d, set())
            filhos.setdefault(d, set()).add(no)

    pronto = [n for n, p in pais.items() if not p]
    heapq.heapify(pronto)
    restantes = {n: len(p) for n, p in pais.items()}
    resultado: List[Hashable] = []
    while pronto:
        no = heapq.heappop(pronto)
        resultado.append(no)
        for f in filhos[no]:
            restantes[f] -= 1
            if restantes[f] == 0:
                heapq.heappush(pronto, f)
    if len(resultado) != len(pais):
        raise CicloDetectado("o grafo possui ciclo")
    return resultado
