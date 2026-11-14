"""Rebalanceamento de carteira por pesos-alvo."""
from __future__ import annotations


def rebalancear(
    quantidades: dict[str, float],
    precos: dict[str, float],
    alvos: dict[str, float],
    caixa: float = 0.0,
    inteiro: bool = False,
) -> dict[str, float]:
    """Devolve a variação de quantidade por ativo (positivo = comprar).

    O patrimônio-base é a soma das posições a mercado mais o caixa. Com
    `inteiro=True` as quantidades são truncadas em direção a zero, de modo que a
    compra nunca excede o caixa disponível."""
    if abs(sum(alvos.values()) - 1.0) > 1e-9:
        raise ValueError("pesos-alvo devem somar 1")
    if any(w < 0 for w in alvos.values()):
        raise ValueError("pesos-alvo não podem ser negativos")
    ativos = set(quantidades) | set(alvos)
    if any(precos.get(a, 0) <= 0 for a in ativos):
        raise ValueError("todos os ativos precisam de preço positivo")
    patrimonio = caixa + sum(quantidades.get(a, 0.0) * precos[a] for a in ativos)
    ordens: dict[str, float] = {}
    for a in sorted(ativos):
        desejada = alvos.get(a, 0.0) * patrimonio / precos[a]
        delta = desejada - quantidades.get(a, 0.0)
        ordens[a] = float(int(delta)) if inteiro else delta
    return ordens


def pesos_atuais(quantidades: dict[str, float], precos: dict[str, float]) -> dict[str, float]:
    valores = {a: q * precos[a] for a, q in quantidades.items()}
    total = sum(valores.values())
    if total <= 0:
        raise ValueError("carteira vazia")
    return {a: v / total for a, v in valores.items()}
