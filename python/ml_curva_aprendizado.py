"""Curva de aprendizado: erro de treino e de validação em função do tamanho do treino."""
from __future__ import annotations

import random
from typing import Callable


def curva_aprendizado(
    ajustar: Callable[[list, list], object],
    prever: Callable[[object, list], list],
    metrica: Callable[[list, list], float],
    X_treino: list, y_treino: list, X_val: list, y_val: list,
    tamanhos: list[int], seed: int = 0,
) -> list[tuple[int, float, float]]:
    """Para cada tamanho n, treina com n amostras e devolve (n, métrica_treino, métrica_val).

    As n amostras são os n primeiros índices de uma permutação fixada pela seed,
    de modo que os subconjuntos são aninhados.
    """
    if len(X_treino) != len(y_treino) or len(X_val) != len(y_val):
        raise ValueError("X e y devem ter o mesmo tamanho")
    ordem = list(range(len(X_treino)))
    random.Random(seed).shuffle(ordem)
    saida = []
    for n in tamanhos:
        if not 1 <= n <= len(X_treino):
            raise ValueError(f"tamanho inválido: {n}")
        idx = ordem[:n]
        Xs, ys = [X_treino[i] for i in idx], [y_treino[i] for i in idx]
        modelo = ajustar(Xs, ys)
        saida.append((n, metrica(ys, prever(modelo, Xs)), metrica(y_val, prever(modelo, X_val))))
    return saida


def diagnostico(curva: list[tuple[int, float, float]], limiar_lacuna: float = 0.1,
                limiar_erro: float = 0.2) -> str:
    """Diagnóstico para métricas de ERRO (menor é melhor) com base no último ponto."""
    _, erro_treino, erro_val = curva[-1]
    if erro_treino > limiar_erro and erro_val > limiar_erro:
        return "subajuste"
    if erro_val - erro_treino > limiar_lacuna:
        return "sobreajuste"
    return "bom"
