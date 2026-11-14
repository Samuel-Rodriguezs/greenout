"""Two-sum e three-sum."""

from __future__ import annotations


def two_sum(nums: list[int], alvo: int) -> tuple[int, int] | None:
    """Índices (i, j), i < j, com nums[i] + nums[j] == alvo; None se não houver."""
    vistos: dict[int, int] = {}
    for j, n in enumerate(nums):
        i = vistos.get(alvo - n)
        if i is not None:
            return i, j
        vistos.setdefault(n, j)
    return None


def three_sum(nums: list[int], alvo: int = 0) -> list[tuple[int, int, int]]:
    """Todas as trincas únicas (ordenadas) de valores que somam o alvo."""
    v = sorted(nums)
    res: list[tuple[int, int, int]] = []
    for i in range(len(v) - 2):
        if i and v[i] == v[i - 1]:
            continue
        esq, dir = i + 1, len(v) - 1
        while esq < dir:
            s = v[i] + v[esq] + v[dir]
            if s < alvo:
                esq += 1
            elif s > alvo:
                dir -= 1
            else:
                res.append((v[i], v[esq], v[dir]))
                esq += 1
                dir -= 1
                while esq < dir and v[esq] == v[esq - 1]:
                    esq += 1
                while esq < dir and v[dir] == v[dir + 1]:
                    dir -= 1
    return res
