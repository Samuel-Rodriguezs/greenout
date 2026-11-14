"""Change Maker Kata: troco com o menor número de moedas/notas (em centavos)."""
from __future__ import annotations

DENOMINACOES_BRL = (10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5)


def fazer_troco(valor: int, denominacoes: tuple[int, ...] = DENOMINACOES_BRL) -> dict[int, int]:
    """Retorna {denominação: quantidade} usando o mínimo de peças.

    Usa programação dinâmica, então funciona para sistemas não canônicos
    (ex.: denominações (1, 3, 4) para 6 -> 3+3). Lança ValueError se impossível.
    """
    if valor < 0:
        raise ValueError("valor não pode ser negativo")
    if not denominacoes or any(d <= 0 for d in denominacoes):
        raise ValueError("denominações devem ser positivas")
    inf = float("inf")
    minimo = [0] + [inf] * valor
    escolha = [0] * (valor + 1)
    for v in range(1, valor + 1):
        for d in denominacoes:
            if d <= v and minimo[v - d] + 1 < minimo[v]:
                minimo[v] = minimo[v - d] + 1
                escolha[v] = d
    if minimo[valor] == inf:
        raise ValueError("não é possível formar o valor")
    troco: dict[int, int] = {}
    while valor > 0:
        d = escolha[valor]
        troco[d] = troco.get(d, 0) + 1
        valor -= d
    return dict(sorted(troco.items(), reverse=True))
