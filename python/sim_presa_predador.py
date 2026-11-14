"""Ecossistema presa-predador: Lotka-Volterra discreto determinístico e versão estocástica."""
from __future__ import annotations

import random


def passo_lv(presas: float, predadores: float, alfa: float, beta: float, delta: float,
             gama: float, dt: float = 0.01) -> tuple[float, float]:
    """Euler: dx = (alfa*x - beta*x*y)dt ; dy = (delta*x*y - gama*y)dt."""
    dx = (alfa * presas - beta * presas * predadores) * dt
    dy = (delta * presas * predadores - gama * predadores) * dt
    return max(0.0, presas + dx), max(0.0, predadores + dy)


def simular_lv(presas: float, predadores: float, passos: int, alfa: float = 1.0, beta: float = 0.1,
               delta: float = 0.075, gama: float = 1.5, dt: float = 0.001) -> list[tuple[float, float]]:
    hist = [(presas, predadores)]
    for _ in range(passos):
        presas, predadores = passo_lv(presas, predadores, alfa, beta, delta, gama, dt)
        hist.append((presas, predadores))
    return hist


def equilibrio(alfa: float, beta: float, delta: float, gama: float) -> tuple[float, float]:
    return gama / delta, alfa / beta


def simular_estocastico(presas: int, predadores: int, passos: int, rng: random.Random,
                        p_nasc: float = 0.1, p_cap: float = 0.002, p_rep: float = 0.001,
                        p_morte: float = 0.1) -> list[tuple[int, int]]:
    """Cada indivíduo tem eventos independentes por passo (nascimento, predação, morte)."""
    hist = [(presas, predadores)]
    for _ in range(passos):
        nasc = sum(rng.random() < p_nasc for _ in range(presas))
        # probabilidade de uma presa ser capturada por algum predador
        p_morrer = 1 - (1 - p_cap) ** predadores
        capturadas = sum(rng.random() < p_morrer for _ in range(presas))
        capturadas = min(capturadas, presas)
        novos_pred = sum(rng.random() < min(1.0, p_rep * presas) for _ in range(predadores)) if capturadas else 0
        mortes = sum(rng.random() < p_morte for _ in range(predadores))
        presas = presas + nasc - capturadas
        predadores = max(0, predadores + novos_pred - mortes)
        hist.append((presas, predadores))
        if presas == 0 and predadores == 0:
            break
    return hist
