"""Futoshiki: quadrado latino n x n com desigualdades entre células vizinhas e dados iniciais."""
from __future__ import annotations

from typing import Optional

Celula = tuple[int, int]
# Desigualdade (a, b): valor em `a` < valor em `b`; as células devem ser vizinhas.
Menor = tuple[Celula, Celula]


def _validar(n: int, menores: list[Menor], dados: dict[Celula, int]) -> None:
    for a, b in menores:
        for c in (a, b):
            if not (0 <= c[0] < n and 0 <= c[1] < n):
                raise ValueError(f"célula fora da grade: {c}")
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            raise ValueError(f"células não vizinhas: {a}, {b}")
    for c, v in dados.items():
        if not (0 <= c[0] < n and 0 <= c[1] < n) or not 1 <= v <= n:
            raise ValueError(f"dado inválido: {c}={v}")


def resolver(n: int, menores: list[Menor], dados: Optional[dict[Celula, int]] = None,
             limite: int = 1) -> list[list[list[int]]]:
    """Lista de até `limite` soluções (cada uma é uma grade). Vazia se não houver solução."""
    dados = dados or {}
    _validar(n, menores, dados)
    dominios: dict[Celula, set[int]] = {
        (r, c): ({dados[(r, c)]} if (r, c) in dados else set(range(1, n + 1)))
        for r in range(n) for c in range(n)
    }
    def propagar(dom: dict[Celula, set[int]]) -> bool:
        """Consistência de arcos para as desigualdades + eliminação por linha/coluna de células fixas."""
        mudou = True
        while mudou:
            mudou = False
            for a, b in menores:
                novo_a = {v for v in dom[a] if any(v < w for w in dom[b])}
                novo_b = {w for w in dom[b] if any(v < w for v in dom[a])}
                if novo_a != dom[a] or novo_b != dom[b]:
                    dom[a], dom[b] = novo_a, novo_b
                    mudou = True
            for (r, c), d in list(dom.items()):
                if not d:
                    return False
                if len(d) == 1:
                    v = next(iter(d))
                    for k in range(n):
                        for outro in ((r, k), (k, c)):
                            if outro != (r, c) and v in dom[outro]:
                                dom[outro] = dom[outro] - {v}
                                if not dom[outro]:
                                    return False
                                mudou = True
        return True

    solucoes: list[list[list[int]]] = []

    def busca(dom: dict[Celula, set[int]]) -> None:
        if len(solucoes) >= limite or not propagar(dom):
            return
        livres = [c for c, d in dom.items() if len(d) > 1]
        if not livres:
            solucoes.append([[next(iter(dom[(r, c)])) for c in range(n)] for r in range(n)])
            return
        cel = min(livres, key=lambda c: (len(dom[c]), c))
        for v in sorted(dom[cel]):
            novo = {c: set(d) for c, d in dom.items()}
            novo[cel] = {v}
            busca(novo)

    busca(dominios)
    return solucoes
