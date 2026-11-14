"""Detector de duplicidade de processos: mesmo número CNJ (em qualquer máscara) ou mesmas partes/objeto."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Registro:
    id: str
    numero: str
    partes: tuple[str, ...] = ()
    objeto: str = ""


def _digitos(numero: str) -> str:
    return re.sub(r"\D", "", numero)


def _texto(s: str) -> frozenset[str]:
    return frozenset(w for w in re.findall(r"\w+", s.casefold()) if len(w) > 2)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def duplicados_por_numero(registros: list[Registro]) -> list[list[str]]:
    """Grupos de ids com o mesmo número (comparando só os dígitos), cada grupo ordenado."""
    grupos: dict[str, list[str]] = defaultdict(list)
    for r in registros:
        d = _digitos(r.numero)
        if d:
            grupos[d].append(r.id)
    return sorted(sorted(g) for g in grupos.values() if len(g) > 1)


def similaridade(a: Registro, b: Registro) -> float:
    """0..1: 60% partes (conjunto de nomes) + 40% objeto (palavras)."""
    pa = frozenset(p.casefold().strip() for p in a.partes)
    pb = frozenset(p.casefold().strip() for p in b.partes)
    return round(0.6 * _jaccard(pa, pb) + 0.4 * _jaccard(_texto(a.objeto), _texto(b.objeto)), 4)


def suspeitos(registros: list[Registro], limite: float = 0.8) -> list[tuple[str, str, float]]:
    """Pares com números diferentes e similaridade >= limite (possível ajuizamento em duplicidade)."""
    if not 0 < limite <= 1:
        raise ValueError("limite deve estar em (0, 1]")
    res: list[tuple[str, str, float]] = []
    for i, a in enumerate(registros):
        for b in registros[i + 1:]:
            if _digitos(a.numero) == _digitos(b.numero):
                continue
            s = similaridade(a, b)
            if s >= limite:
                res.append((a.id, b.id, s))
    return sorted(res, key=lambda t: (-t[2], t[0], t[1]))
