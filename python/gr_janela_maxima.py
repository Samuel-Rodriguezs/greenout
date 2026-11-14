"""Máximo (e mínimo) de janela deslizante com deque monotônico, O(n)."""

from __future__ import annotations

from collections import deque


def _janela(nums: list[int], k: int, melhor) -> list[int]:
    if k <= 0:
        raise ValueError("k deve ser positivo")
    if k > len(nums):
        return []
    dq: deque[int] = deque()  # índices; valores em ordem monotônica
    res: list[int] = []
    for i, n in enumerate(nums):
        while dq and melhor(n, nums[dq[-1]]):
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res


def janela_maxima(nums: list[int], k: int) -> list[int]:
    return _janela(nums, k, lambda novo, velho: novo >= velho)


def janela_minima(nums: list[int], k: int) -> list[int]:
    return _janela(nums, k, lambda novo, velho: novo <= velho)
