"""Deduplicação de registros: chaves normalizadas e agrupamento por similaridade."""
from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher
from typing import Any, Sequence


def normalizar(texto: Any) -> str:
    """Minúsculas, sem acentos, espaços colapsados; None vira ''."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.lower().split())


def _chave(reg: dict[str, Any], chaves: Sequence[str], norm: bool) -> tuple:
    return tuple(normalizar(reg.get(c)) if norm else reg.get(c) for c in chaves)


def deduplicar(
    registros: Sequence[dict[str, Any]],
    chaves: Sequence[str],
    manter: str = "primeiro",
    normalizar_chaves: bool = True,
) -> list[dict[str, Any]]:
    """Remove registros com a mesma chave, mantendo o primeiro ou o último de cada grupo."""
    if manter not in ("primeiro", "ultimo"):
        raise ValueError("manter deve ser 'primeiro' ou 'ultimo'")
    if not chaves:
        raise ValueError("informe ao menos uma chave")
    escolhidos: dict[tuple, int] = {}
    for i, r in enumerate(registros):
        k = _chave(r, chaves, normalizar_chaves)
        if manter == "ultimo" or k not in escolhidos:
            escolhidos[k] = i
    return [registros[i] for i in sorted(escolhidos.values())]


def grupos_duplicados(
    registros: Sequence[dict[str, Any]], chaves: Sequence[str], normalizar_chaves: bool = True
) -> list[list[int]]:
    """Grupos (índices) com 2 ou mais registros de mesma chave."""
    mapa: dict[tuple, list[int]] = {}
    for i, r in enumerate(registros):
        mapa.setdefault(_chave(r, chaves, normalizar_chaves), []).append(i)
    return [idx for idx in mapa.values() if len(idx) > 1]


def similaridade(a: str, b: str) -> float:
    return SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()


def agrupar_similares(textos: Sequence[str], limiar: float = 0.85) -> list[list[int]]:
    """Agrupamento guloso: cada texto entra no primeiro grupo cujo representante é similar."""
    if not 0 <= limiar <= 1:
        raise ValueError("limiar deve estar em [0, 1]")
    grupos: list[list[int]] = []
    for i, t in enumerate(textos):
        for g in grupos:
            if similaridade(textos[g[0]], t) >= limiar:
                g.append(i)
                break
        else:
            grupos.append([i])
    return grupos


def deduplicar_fuzzy(
    registros: Sequence[dict[str, Any]], campo: str, limiar: float = 0.9
) -> list[dict[str, Any]]:
    """Mantém o primeiro registro de cada grupo de valores similares em `campo`."""
    grupos = agrupar_similares([str(r.get(campo) or "") for r in registros], limiar)
    return [registros[g[0]] for g in sorted(grupos, key=lambda g: g[0])]
