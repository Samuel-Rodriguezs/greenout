"""Métricas de avaliação: accuracy, precision, recall, F1, ROC-AUC, MSE, R²."""
from __future__ import annotations


def _checar(a: list, b: list) -> None:
    if len(a) != len(b):
        raise ValueError("listas devem ter o mesmo tamanho")
    if not a:
        raise ValueError("listas vazias")


def acuracia(y: list, previsto: list) -> float:
    _checar(y, previsto)
    return sum(a == b for a, b in zip(y, previsto)) / len(y)


def matriz_confusao(y: list[int], previsto: list[int], positivo: int = 1) -> tuple[int, int, int, int]:
    """Retorna (VP, FP, FN, VN)."""
    _checar(y, previsto)
    vp = sum(a == positivo and b == positivo for a, b in zip(y, previsto))
    fp = sum(a != positivo and b == positivo for a, b in zip(y, previsto))
    fn = sum(a == positivo and b != positivo for a, b in zip(y, previsto))
    return vp, fp, fn, len(y) - vp - fp - fn


def precisao(y: list[int], previsto: list[int], positivo: int = 1) -> float:
    vp, fp, _, _ = matriz_confusao(y, previsto, positivo)
    return vp / (vp + fp) if vp + fp else 0.0


def revocacao(y: list[int], previsto: list[int], positivo: int = 1) -> float:
    vp, _, fn, _ = matriz_confusao(y, previsto, positivo)
    return vp / (vp + fn) if vp + fn else 0.0


def f1(y: list[int], previsto: list[int], positivo: int = 1) -> float:
    p, r = precisao(y, previsto, positivo), revocacao(y, previsto, positivo)
    return 2 * p * r / (p + r) if p + r else 0.0


def roc_auc(y: list[int], escores: list[float]) -> float:
    """AUC via estatística de Mann-Whitney (empates contam 0,5)."""
    _checar(y, escores)
    pos = [s for r, s in zip(y, escores) if r == 1]
    neg = [s for r, s in zip(y, escores) if r != 1]
    if not pos or not neg:
        raise ValueError("são necessárias as duas classes")
    total = 0.0
    for p in pos:
        for n in neg:
            total += 1.0 if p > n else 0.5 if p == n else 0.0
    return total / (len(pos) * len(neg))


def mse(y: list[float], previsto: list[float]) -> float:
    _checar(y, previsto)
    return sum((a - b) ** 2 for a, b in zip(y, previsto)) / len(y)


def r2(y: list[float], previsto: list[float]) -> float:
    _checar(y, previsto)
    media = sum(y) / len(y)
    ss_tot = sum((a - media) ** 2 for a in y)
    ss_res = sum((a - b) ** 2 for a, b in zip(y, previsto))
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return 1 - ss_res / ss_tot
