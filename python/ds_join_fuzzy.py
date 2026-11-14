"""Join fuzzy entre tabelas (listas de dicts) por similaridade de texto."""
from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher
from typing import Any, Sequence


def _norm(t: Any) -> str:
    s = unicodedata.normalize("NFD", "" if t is None else str(t))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def similaridade(a: Any, b: Any) -> float:
    """Maior entre a razão direta e a razão com palavras ordenadas."""
    na, nb = _norm(a), _norm(b)
    direta = SequenceMatcher(None, na, nb).ratio()
    ordenada = SequenceMatcher(None, " ".join(sorted(na.split())), " ".join(sorted(nb.split()))).ratio()
    return max(direta, ordenada)


def join_fuzzy(
    esquerda: Sequence[dict[str, Any]],
    direita: Sequence[dict[str, Any]],
    chave_esq: str,
    chave_dir: str,
    limiar: float = 0.8,
    how: str = "inner",
    unico: bool = False,
) -> list[dict[str, Any]]:
    """Cada linha da esquerda recebe a melhor correspondência da direita (score >= limiar).

    Adiciona o campo `_similaridade`. Com `unico`, cada linha da direita é usada no máximo
    uma vez, priorizando os pares de maior score.
    """
    if how not in ("inner", "left"):
        raise ValueError("how deve ser 'inner' ou 'left'")
    if not 0 <= limiar <= 1:
        raise ValueError("limiar deve estar em [0, 1]")
    pares = []
    for i, le in enumerate(esquerda):
        for j, ld in enumerate(direita):
            s = similaridade(le.get(chave_esq), ld.get(chave_dir))
            if s >= limiar:
                pares.append((s, i, j))
    escolha: dict[int, tuple[float, int]] = {}
    if unico:
        usados: set[int] = set()
        for s, i, j in sorted(pares, key=lambda p: (-p[0], p[1], p[2])):
            if i not in escolha and j not in usados:
                escolha[i] = (s, j)
                usados.add(j)
    else:
        for s, i, j in sorted(pares, key=lambda p: (-p[0], p[1], p[2])):
            escolha.setdefault(i, (s, j))

    colunas_esq = set()
    for l in esquerda:
        colunas_esq |= set(l)
    saida: list[dict[str, Any]] = []
    for i, le in enumerate(esquerda):
        if i in escolha:
            s, j = escolha[i]
            extra = {(k + "_dir" if k in colunas_esq else k): v for k, v in direita[j].items()}
            saida.append({**le, **extra, "_similaridade": s})
        elif how == "left":
            saida.append({**le, "_similaridade": None})
    return saida
